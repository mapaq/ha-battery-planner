"""Battery Planner main class"""

import logging
import json
import importlib
from datetime import datetime, timedelta, time

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import EVENT_NEW_DATA
from .charge_plan import ChargePlan
from .battery import Battery
from .battery_api_interface import BatteryApiInterface

_LOGGER = logging.getLogger(__name__)

API_PATH = "custom_components.battery_planner.api"
SECRETS_PATH = "secrets.json"


class BatteryPlanner:
    """Main class to handle data and push updates"""

    # The price difference between charge hour and discharge hour
    # must be higher than this to create a schedule for those hours
    _price_margin: float
    _cheap_price: float

    _hass: HomeAssistant
    _active_schedule: ChargePlan
    _battery: Battery
    _battery_api: BatteryApiInterface

    def __init__(
        self,
        hass: HomeAssistant,
        battery: Battery,
        price_margin: float,
        cheap_price: float,
    ):
        self._hass = hass
        self._active_schedule = None
        self._battery = battery
        self._price_margin = price_margin
        self._cheap_price = cheap_price
        self._battery_api = create_api_instance_from_secrets_file(hass)

    async def reschedule(
        self,
        battery_state_of_charge: float,
        prices_today: list[float],
        prices_tomorrow: list[float],
    ) -> None:
        """Get future prices and create new schedule"""
        _LOGGER.info(
            "Rescheduling battery, battery state of charge = %s",
            battery_state_of_charge,
        )
        _LOGGER.debug("Prices today = %s", prices_today)
        _LOGGER.debug("Prices tomorrow = %s", prices_tomorrow)

        self._battery.set_soc(battery_state_of_charge)

        active_charge_plan = await self._get_active_schedule()
        hourly_prices = map_prices_to_hour(prices_today, prices_tomorrow)
        hourly_prices = self._get_future_unscheduled_hours(
            hourly_prices, active_charge_plan
        )
        charge_plan = self._create_charge_plan_based_on_prices(hourly_prices)

        _LOGGER.debug("New charge plan will be scheduled:\n%s", charge_plan)

        schedule_succeeded = await self._battery_api.schedule_battery(charge_plan)
        if schedule_succeeded:
            _LOGGER.info("Battery was scheduled with a new charge plan")
        else:
            _LOGGER.error("Failed to schedule battery with new charge plan")
        await self.get_active_schedule(refresh=True)

    async def get_active_schedule(self, refresh: bool = False) -> ChargePlan:
        """Get the currently active schedule from API"""
        if self._active_schedule is None or refresh is True:
            self._active_schedule = await self._get_active_schedule()
        return self._active_schedule

    async def _get_active_schedule(self) -> ChargePlan:
        active_charge_plan = await self._battery_api.get_active_charge_plan()
        if isinstance(active_charge_plan, ChargePlan):
            # TODO: Add prices to the fetched charge plan
            async_dispatcher_send(self._hass, EVENT_NEW_DATA)
        else:
            _LOGGER.error("Could not fetch the active charge plan from the battery")
        return active_charge_plan

    def _get_future_unscheduled_hours(
        self, hourly_prices: dict[datetime, object], active_charge_plan: ChargePlan
    ) -> dict[datetime, object]:
        """Remove the passed hours from a dict and return the future hours"""
        now = datetime.now()

        last_scheduled_hour = now
        for hour_iso, entry in active_charge_plan.scheduled_hours().items():
            hour = datetime.fromisoformat(hour_iso)
            power = entry[ChargePlan.KEY_POWER]
            if power != 0:
                if hour > now:
                    # Energy per hour (Wh) is equivalent to average power (W) for one hour
                    # Negating power since -power means charge (consume) and +power means discharge (produce)
                    self._battery.add_energy(-power)
                last_scheduled_hour = hour

        future_hours = {}
        for hour, value in hourly_prices.items():
            if hour > now and hour > last_scheduled_hour:
                future_hours[hour] = value
        return future_hours

    def _create_charge_plan_based_on_prices(
        self,
        hourly_prices: dict[datetime, float],
    ) -> ChargePlan:
        """Charge plan is created for the period specified by the provided hours

        The battery may have a minimum state of charge setting, which will decrease the actual available
        capacity of the battery. However, we can set the battery_capacity to ~5% higher than the
        actual available capacity to ensure that it is fully charged and discharged. Therefore it is
        fine to use the full capacity of the battery if the minimum SoC is set to e.g. 5%.

        hourly_prices - A dict with the time (hour) and electricity price (price/kWh) for that hour
        battery_capacity - The full capacity of the battery (Wh)
        max_charge_power - The maximum allowed charge level to be planned (W)
        max_discharge_power - The maximum allowed discharge level to be planned (W)

        Returns a plan with all 0 W if the price margin is to low"""

        hourly_prices_sorted_by_hour: dict[datetime, float] = {
            key: val
            for key, val in sorted(hourly_prices.items(), key=lambda ele: ele[0])
        }
        power_levels: dict[datetime, int] = {
            key: 0
            for key, val in sorted(
                hourly_prices_sorted_by_hour.items(), key=lambda ele: ele[0]
            )
        }
        hourly_prices_sorted_by_lowest_price: dict[datetime, float] = {
            key: val
            for key, val in sorted(
                hourly_prices_sorted_by_hour.items(), key=lambda ele: ele[1]
            )
        }
        hourly_prices_sorted_by_highest_price: dict[datetime, float] = {
            key: val
            for key, val in sorted(
                hourly_prices_sorted_by_hour.items(),
                key=lambda ele: ele[1],
                reverse=True,
            )
        }

        last_charged_hour = self._charge_at_lowest_priced_hours(
            hourly_prices_sorted_by_highest_price,
            hourly_prices_sorted_by_lowest_price,
            power_levels,
        )

        self._discharge_at_highest_priced_hours(
            hourly_prices_sorted_by_highest_price, power_levels, last_charged_hour
        )

        charge_plan = _create_charge_plan(hourly_prices, power_levels)

        if charge_plan.is_empty_plan():
            self._charge_if_super_cheap_prices(
                hourly_prices_sorted_by_lowest_price, power_levels
            )
            charge_plan = _create_charge_plan(hourly_prices, power_levels)

        return charge_plan

    def _charge_at_lowest_priced_hours(
        self,
        hourly_prices_sorted_by_highest_price: dict[datetime, float],
        hourly_prices_sorted_by_lowest_price: dict[datetime, float],
        power_levels: dict[datetime, int],
    ) -> datetime:

        last_charged_hour: datetime = datetime.now()

        # Since we are creating one schedule for each hour, the power level is the
        # same as added energy for that hour, i.e. Power (W) during one hour = Energy (Wh)
        for (
            discharge_hour,
            discharge_price,
        ) in hourly_prices_sorted_by_highest_price.items():
            for (
                charge_hour,
                charge_price,
            ) in hourly_prices_sorted_by_lowest_price.items():
                if (
                    (charge_hour < discharge_hour)
                    and (discharge_price - charge_price > self._price_margin)
                    and (not self._battery.is_full())
                    and (power_levels[charge_hour] == 0)
                ):
                    power_levels[charge_hour] = self._battery.charge_max()
                    last_charged_hour = charge_hour
        return last_charged_hour

    def _discharge_at_highest_priced_hours(
        self,
        hourly_prices_sorted_by_highest_price: dict[datetime, float],
        power_levels: dict[datetime, int],
        last_charged_hour: datetime,
    ):
        for discharge_hour, price in hourly_prices_sorted_by_highest_price.items():
            # FIXME: Won't discharge when charged at negative price and discharge price is below PRICE_MARGIN
            # Maybe store the chargeing price as an attribute on sensor to use when not discharged in the same day
            if (
                (self._battery.remaining_energy_above_lower_soc_limit() > 0)
                and (price >= self._price_margin)
                and (discharge_hour > last_charged_hour)
            ):
                power_levels[discharge_hour] = self._battery.discharge_max()

    def _charge_if_super_cheap_prices(
        self,
        hourly_prices_sorted_by_lowest_price: dict[datetime, float],
        power_levels: dict[datetime, int],
    ):
        for (
            charge_hour,
            charge_price,
        ) in hourly_prices_sorted_by_lowest_price.items():
            if (
                (charge_price < self._cheap_price)
                and (not self._battery.is_full())
                and (power_levels[charge_hour] == 0)
            ):
                power_levels[charge_hour] = self._battery.charge_max()


def map_prices_to_hour(
    prices_today: list[float], prices_tomorrow: list[float]
) -> dict[datetime, float]:
    """Get electricity prices from nordpool integration"""
    hourly_prices: dict[datetime, float] = {}
    now = datetime.now()
    today_midnight = datetime.combine(now.date(), time(0))
    hour = today_midnight
    for price in prices_today + prices_tomorrow:
        hourly_prices[hour] = price
        hour += timedelta(hours=1)
    return hourly_prices


def create_api_instance_from_secrets_file(hass: HomeAssistant):
    """Create battery api instance from the api privided in secrets file"""
    secrets_json = get_secrets()
    api_name: str = secrets_json.get("api")
    api_module = importlib.import_module(f"{API_PATH}.{api_name}.{api_name}")
    class_name = class_name_from_module_name(api_name)
    cls = getattr(api_module, class_name)
    battery_api: BatteryApiInterface = cls(secrets_json, hass)
    return battery_api


def get_secrets() -> dict[str:str]:
    """Get name of the API to be used, specified in the secrets file"""
    with open(SECRETS_PATH, encoding="utf-8") as secrets_file:
        return json.load(secrets_file).get("battery_planner")


def class_name_from_module_name(module_name: str) -> str:
    """Create a PascalCase class name from a snake_case module name"""
    class_name = ""
    words = module_name.split("_")
    for word in words:
        class_name += word.capitalize()
    return class_name


def _create_charge_plan(hourly_prices, power_levels) -> ChargePlan:
    charge_plan = ChargePlan()
    for hour, power in power_levels.items():
        charge_plan.add(hour=hour, power=power, price=hourly_prices[hour])
    return charge_plan

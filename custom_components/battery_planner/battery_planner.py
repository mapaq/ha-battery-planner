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


class BatteryPlanner:
    """Main class to handle data and push updates"""

    # The price difference between charge hour and discharge hour
    # must be higher than this to create a schedule for those hours
    # TODO: Make configurable in configuration.yaml
    PRICE_MARGIN: float = 1.0

    _hass: HomeAssistant
    _active_schedule: ChargePlan
    _battery: Battery
    _battery_api: BatteryApiInterface

    def __init__(self, hass: HomeAssistant):
        self._hass = hass
        self._active_schedule = None
        # TODO: Make configurable
        self._battery = Battery(
            capacity=7700,
            soc_limit=0.05,
            max_charge_power=3000,
            max_discharge_power=3000,
        )
        self._battery_api = create_api_instance_from_secrets_file()
        self._battery_api.login()

    async def reschedule(
        self,
        battery_state_of_charge: float,
        prices_today: list[float],
        prices_tomorrow: list[float],
    ) -> None:
        """Get future prices and create new schedule"""
        _LOGGER.debug(
            "Rescheduling battery, battery state of charge = %s",
            battery_state_of_charge,
        )
        self._battery.set_soc(battery_state_of_charge)
        hourly_prices = map_prices_to_hour(prices_today, prices_tomorrow)
        charge_plan = self._create_charge_plan(hourly_prices)

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
            async_dispatcher_send(self._hass, EVENT_NEW_DATA)
        else:
            _LOGGER.error("Could not fetch the active charge plan from the battery")
        return active_charge_plan

    def _create_charge_plan(
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

        hourly_prices = get_future_hours(hourly_prices)

        hourly_prices_sorted_by_hour = {
            key: val
            for key, val in sorted(hourly_prices.items(), key=lambda ele: ele[0])
        }
        power_levels = {
            key: 0
            for key, val in sorted(
                hourly_prices_sorted_by_hour.items(), key=lambda ele: ele[0]
            )
        }
        hourly_prices_sorted_by_lowest_price = {
            key: val
            for key, val in sorted(
                hourly_prices_sorted_by_hour.items(), key=lambda ele: ele[1]
            )
        }
        hourly_prices_sorted_by_highest_price = {
            key: val
            for key, val in sorted(
                hourly_prices_sorted_by_hour.items(),
                key=lambda ele: ele[1],
                reverse=True,
            )
        }

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
                    and (discharge_price - charge_price > self.PRICE_MARGIN)
                    and (self._battery.energy < self._battery.capacity)
                    and (power_levels[charge_hour] == 0)
                ):
                    power_levels[charge_hour] = self._battery.charge()
                # TODO: If yield is too low, won't charge. But should charge and not discharge
                # if absolute price is very low, like < 0.2 SEK or something. To be prepared to
                # discharge when price rises again.

        for (
            discharge_hour,
            discharge_price,
        ) in hourly_prices_sorted_by_highest_price.items():
            if self._battery.remaining_energy_above_soc_limit() > 0:
                power_levels[discharge_hour] = self._battery.discharge()

        charge_plan = ChargePlan()
        for hour, power in power_levels.items():
            charge_plan.add(hour=hour, power=power, price=hourly_prices[hour])

        return charge_plan


def get_future_hours(hours: dict[datetime, object]):
    """Remove the passed hours from a dict and return the future hours"""
    now = datetime.now()
    future_hours = {}
    for hour, value in hours.items():
        if now < hour:
            future_hours[hour] = value
    return future_hours


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


def create_api_instance_from_secrets_file():
    """Create battery api instance from the api privided in secrets file"""
    secrets_json = get_secrets()
    api_name = secrets_json.get("api")
    api_module = importlib.import_module(f"{API_PATH}.{api_name}.{api_name}")
    cls = getattr(api_module, "ExampleBatteryApi")
    battery_api: BatteryApiInterface = cls(secrets_json)
    return battery_api


def get_secrets() -> dict[str:str]:
    """Get name of the API to be used, specified in the secrets file"""
    secrets_path = "custom_components/battery_planner/secrets.json"
    with open(secrets_path, encoding="utf-8") as secrets_file:
        return json.load(secrets_file)

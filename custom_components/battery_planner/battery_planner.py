"""Battery Planner main class"""

import logging
import json
import importlib
from datetime import datetime, timedelta, time

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import EVENT_NEW_DATA
from .charge_plan import ChargePlan
from .charge_hour import ChargeHour
from .planner import Planner, create_empty_plan
from .battery import Battery
from .battery_api_interface import BatteryApiInterface

_LOGGER = logging.getLogger(__name__)

API_PATH = "custom_components.battery_planner.api"
SECRETS_PATH = "secrets.json"


class BatteryPlanner:
    """Main class to handle data and push updates"""

    _latest_prices: dict[str, list[float]]

    _hass: HomeAssistant
    _active_charge_plan: ChargePlan
    _battery: Battery
    _battery_api: BatteryApiInterface

    def __init__(
        self,
        hass: HomeAssistant,
        battery: Battery,
    ):
        self._hass = hass
        self._active_charge_plan = None  # type: ignore
        self._battery = battery
        self._latest_prices = {}
        self._battery_api = create_api_instance_from_secrets_file(hass)

    async def stop(self) -> None:
        """Stop the battery"""
        stop_succeeded = await self._battery_api.stop()
        if stop_succeeded:
            _LOGGER.info("Battery was stopped")
        else:
            _LOGGER.error("Failed to stop battery")
        await self.refresh()

    async def clear(self) -> None:
        """Clear the battery schedule"""
        stop_succeeded = await self._battery_api.clear()
        if stop_succeeded:
            _LOGGER.info("Battery schedule was cleared")
        else:
            _LOGGER.error("Failed to clear the battery schedule")
        await self.refresh()

    async def charge_now(
        self, battery_state_of_charge: float, power: int, use_limit: bool
    ) -> None:
        """Charge or discharge the battery with provided power, starting immediately"""
        current_hour: int = datetime.now().hour
        charge_plan = create_empty_plan(start_hour=current_hour)
        shall_discharge: bool = power > 0

        battery = Battery(
            self._battery.get_capacity(),
            self._battery.get_max_charge_power(),
            self._battery.get_max_discharge_power(),
            self._battery.get_upper_soc_limit(),
            self._battery.get_lower_soc_limit(),
        )
        battery.set_soc(battery_state_of_charge)

        if use_limit:
            if shall_discharge:
                power = min(battery.get_max_discharge_power(), abs(power))
            else:
                power = -min(battery.get_max_charge_power(), abs(power))

        charge_plan.add_charge_hour(ChargeHour(current_hour, 0.0, 0.0, power))

        next_hour = current_hour + 1
        if shall_discharge:
            while not battery.is_empty():
                charge_hour = ChargeHour(next_hour, 0.0, 0.0, power)
                charge_hour.set_power(battery.discharge(abs(power)))
                charge_plan.add_charge_hour(charge_hour)
                next_hour += 1
        else:
            while not battery.is_full():
                charge_hour = ChargeHour(next_hour, 0.0, 0.0, power)
                charge_hour.set_power(battery.charge(abs(power), charge_hour))
                charge_plan.add_charge_hour(charge_hour)
                next_hour += 1

        charge_succeeded = await self._battery_api.schedule_battery(charge_plan)
        if charge_succeeded:
            _LOGGER.info("Battery started charging/discharging with power %s", power)
        else:
            _LOGGER.error("Failed to start charging/discharging of the battery")
        await self.refresh()

    async def refresh(self) -> None:
        """Refresh the sensor"""
        await self.get_active_charge_plan(refresh=True)

    async def reschedule(
        self,
        battery_state_of_charge: float,
        import_prices: list[float],
        export_prices: list[float],
        battery_cycle_cost: float,
        price_margin: float,
        low_price_threshold: float,
    ) -> None:
        """Get future prices and create new schedule"""
        _LOGGER.info(
            "Rescheduling battery, battery state of charge = %s%%",
            battery_state_of_charge,
        )
        _LOGGER.debug("Import prices = %s", import_prices)
        _LOGGER.debug("Export prices = %s", export_prices)
        _LOGGER.debug("Battery cycle cost = %s", battery_cycle_cost)
        _LOGGER.debug("Price margin = %s", price_margin)
        self._latest_prices["import"] = import_prices
        self._latest_prices["export"] = export_prices

        planner: Planner = Planner(
            battery_cycle_cost,
            price_margin,
            low_price_threshold,
        )

        battery = Battery(
            self._battery.get_capacity(),
            self._battery.get_max_charge_power(),
            self._battery.get_max_discharge_power(),
            self._battery.get_upper_soc_limit(),
            self._battery.get_lower_soc_limit(),
        )
        battery.set_soc(battery_state_of_charge)

        next_hour = (datetime.now() + timedelta(hours=1)).hour
        if next_hour == 0:
            next_hour = 24

        charge_plan = planner.create_price_arbitrage_plan(
            battery,
            import_prices,
            export_prices,
            next_hour,
        )

        _LOGGER.debug("New charge plan will be scheduled:\n%s", charge_plan)

        schedule_succeeded = await self._battery_api.schedule_battery(charge_plan)
        if schedule_succeeded:
            _LOGGER.info("Battery was scheduled with a new charge plan")
        else:
            _LOGGER.error("Failed to schedule battery with new charge plan")
        await self.get_active_charge_plan(refresh=True)

    async def get_active_charge_plan(self, refresh: bool = False) -> ChargePlan:
        """Get the currently active schedule from API"""
        if self._active_charge_plan is None or refresh is True:
            active_charge_plan = await self._get_active_charge_plan()
            if isinstance(active_charge_plan, ChargePlan):
                self._active_charge_plan = active_charge_plan
                async_dispatcher_send(self._hass, EVENT_NEW_DATA)
            else:
                _LOGGER.error("Could not fetch the active charge plan from the battery")
        return self._active_charge_plan

    async def _get_active_charge_plan(self) -> ChargePlan:
        active_charge_plan = await self._battery_api.get_active_charge_plan()
        for hour in active_charge_plan.get_hours_list():
            if "import" in self._latest_prices:
                hour.set_import_price(self._latest_prices["import"][hour.get_index()])
            if "export" in self._latest_prices:
                hour.set_export_price(self._latest_prices["export"][hour.get_index()])
        return active_charge_plan


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
    api_name: str = str(secrets_json.get("api"))
    api_module = importlib.import_module(f"{API_PATH}.{api_name}.{api_name}")
    class_name = class_name_from_module_name(api_name)
    cls = getattr(api_module, class_name)
    battery_api: BatteryApiInterface = cls(secrets_json, hass)
    return battery_api


def get_secrets() -> dict[str, str]:
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

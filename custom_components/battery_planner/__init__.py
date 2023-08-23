"""Battery Planner integration"""

import logging

from homeassistant.core import HomeAssistant, Config

from .const import DOMAIN
from .battery_planner import BatteryPlanner
from .battery import Battery


_LOGGER = logging.getLogger(__name__)


NAME = DOMAIN
VERSION = "0.1.3"  # TODO: Get version from manifest.json
ISSUEURL = "https://github.com/mapaq/ha-battery-planner/issues"

STARTUP = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom component
If you have any issues with this you need to open an issue here:
{ISSUEURL}
-------------------------------------------------------------------
"""


async def _create_battery_planner_and_add_to_hass(
    hass: HomeAssistant, hass_config: Config
) -> bool:
    """Set up using yaml config file."""
    if DOMAIN not in hass.data:
        config = hass_config.get("battery_planner")  # type: ignore
        battery = Battery(
            capacity=config.get("capacity"),
            max_charge_power=config.get("max_charge_power"),
            max_discharge_power=config.get("max_discharge_power"),
            upper_soc_limit=config.get("upper_soc_limit"),
            lower_soc_limit=config.get("lower_soc_limit"),
        )

        battery_planner = BatteryPlanner(
            hass=hass,
            battery=battery,
            cheap_price=config.get("cheap_price"),
        )
        hass.data[DOMAIN] = battery_planner
        _LOGGER.debug("Added %s to hass.data", DOMAIN)
    return True


async def async_setup(hass: HomeAssistant, hass_config: Config) -> bool:
    """Set up using yaml config file."""

    instance_created = await _create_battery_planner_and_add_to_hass(hass, hass_config)
    battery_planner: BatteryPlanner = hass.data[DOMAIN]

    # service: battery_planner.reschedule
    # data:
    #     battery_soc: 0.09
    #     import_prices_today: '{{ state_attr("sensor.electricity_price_buy", "today") }}'
    #     import_prices_tomorrow: '{{ state_attr("sensor.electricity_price_buy", "tomorrow") }}'
    #     export_prices_today: '{{ state_attr("sensor.electricity_price_sell", "today") }}'
    #     export_prices_tomorrow: '{{ state_attr("sensor.electricity_price_sell", "tomorrow") }}'
    async def service_call_reschedule(service_call):
        """Get future prices and create new schedule"""
        _LOGGER.debug("%s: service_call_reschedule", DOMAIN)
        battery_soc: float = service_call.data.get("battery_soc", 0.0)
        import_prices_today: list[float] = service_call.data.get(
            "import_prices_today", []
        )
        import_prices_tomorrow: list[float] = service_call.data.get(
            "import_prices_tomorrow", []
        )
        export_prices_today: list[float] = service_call.data.get(
            "export_prices_today", []
        )
        export_prices_tomorrow: list[float] = service_call.data.get(
            "export_prices_tomorrow", []
        )
        await battery_planner.reschedule(
            battery_soc,
            import_prices_today + import_prices_tomorrow,
            export_prices_today + export_prices_tomorrow,
        )

    async def service_call_stop(service_call):
        """Stop the battery"""
        _LOGGER.debug("%s: service_call_stop", DOMAIN)
        await battery_planner.stop()

    async def service_call_clear(service_call):
        """Stop the battery"""
        _LOGGER.debug("%s: service_call_clear", DOMAIN)
        await battery_planner.clear()

    async def service_call_charge(service_call):
        """Charge the battery now"""
        battery_soc: float = service_call.data.get("battery_soc", 0.0)
        power: int = service_call.data.get("power", 4000)
        _LOGGER.debug("%s: service_call_charge", DOMAIN)
        await battery_planner.charge(battery_soc, power)

    async def service_call_refresh(service_call):
        """Refresh the sensor"""
        _LOGGER.debug("%s: service_call_refresh", DOMAIN)
        await battery_planner.refresh()

    hass.services.async_register(DOMAIN, "reschedule", service_call_reschedule)
    hass.services.async_register(DOMAIN, "stop", service_call_stop)
    hass.services.async_register(DOMAIN, "clear", service_call_clear)
    hass.services.async_register(DOMAIN, "charge", service_call_charge)
    hass.services.async_register(DOMAIN, "refresh", service_call_refresh)

    return instance_created

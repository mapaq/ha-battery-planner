"""Battery Planner integration"""

import logging

from homeassistant.core import HomeAssistant, Config

from .const import DOMAIN
from .battery_planner import BatteryPlanner


_LOGGER = logging.getLogger(__name__)


NAME = DOMAIN
VERSION = "0.1.0"
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


async def _dry_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up using yaml config file."""
    if DOMAIN not in hass.data:
        battery_planner = BatteryPlanner(hass)
        hass.data[DOMAIN] = battery_planner
        _LOGGER.debug("Added %s to hass.data", DOMAIN)
    return True


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up using yaml config file."""
    _LOGGER.debug("%s: async_setup", DOMAIN)

    async def service_call_reschedule(service_call):
        """Get future prices and create new schedule
        Example call:

        service: "battery_planner.reschedule"
        data:
          battery_soc: 7

        """
        _LOGGER.debug("%s: service_call_reschedule", DOMAIN)
        battery_soc: float = service_call.data.get("battery_soc", 0.0)
        battery_planner: BatteryPlanner = hass.data[DOMAIN]
        await battery_planner.reschedule(battery_soc)

    hass.services.async_register(DOMAIN, "reschedule", service_call_reschedule)

    return await _dry_setup(hass, config)

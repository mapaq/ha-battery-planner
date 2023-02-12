"""Battery Planner integration"""

import logging

from homeassistant.core import HomeAssistant, Config

from .const import DOMAIN
from .battery_planner import BatteryPlanner


_LOGGER = logging.getLogger(__name__)


NAME = DOMAIN
VERSION = "0.1.1"  # TODO: Get version from manifest.json
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

    # TODO: Make a "stop" service, the stop service is handled differently
    # by each API, so just call "stop" to the API to make the battery stop charging
    # and keep being stopped until started or rescheduled again

    # TODO: Make a "start" service that will charge the battery up to 100% and then set to idle (0 W)

    async def service_call_reschedule(service_call):
        """Get future prices and create new schedule"""

        _LOGGER.debug("%s: service_call_reschedule", DOMAIN)
        battery_soc: float = service_call.data.get("battery_soc", 0.0)
        prices_today: float = service_call.data.get("prices_today", None)
        prices_tomorrow: float = service_call.data.get("prices_tomorrow", None)
        battery_planner: BatteryPlanner = hass.data[DOMAIN]
        await battery_planner.reschedule(
            battery_state_of_charge=battery_soc,
            prices_today=prices_today,
            prices_tomorrow=prices_tomorrow,
        )

    hass.services.async_register(DOMAIN, "reschedule", service_call_reschedule)

    return await _dry_setup(hass, config)

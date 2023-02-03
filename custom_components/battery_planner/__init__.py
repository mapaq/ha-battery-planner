"""Battery Planner integration"""
import logging

import voluptuous as vol
from homeassistant.core import Config, HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util import dt as dt_utils

DOMAIN = "battery_planner"
_LOGGER = logging.getLogger(__name__)
EVENT_NEW_DATA = "battery_schedule_received"

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

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


class BatteryPlanner:
    """Main class to handle data and push updates"""

    def __init__(self, hass: HomeAssistant):
        self._hass = hass
        self._last_tick = None
        self._active_schedule = None
        self.currency = []
        self.listeners = []

    async def reschedule(self, battery_state_of_charge: float = None) -> None:
        """Get future prices and create new schedule"""
        _LOGGER.debug(
            "Rescheduling battery, battery state of charge = %s",
            battery_state_of_charge,
        )
        await self._reschedule()

    async def _reschedule(self) -> None:
        _LOGGER.debug("calling _reschedule")

        active_schedule = await self._get_active_schedule()
        if active_schedule:
            self._active_schedule = active_schedule
        else:
            _LOGGER.error("Could not fetch battery charge schedule")

    async def get_active_schedule(self, refresh: bool = False):
        """Get the currently active schedule from API"""
        if self._active_schedule is None or refresh is True:
            return await self._get_active_schedule()
        return self._active_schedule

    async def _get_active_schedule(self):
        response = 12.03
        if response is not None:
            self._active_schedule = response
            async_dispatcher_send(self._hass, EVENT_NEW_DATA)
        return self._active_schedule


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
        battery_soc = service_call.data.get("battery_soc", 0)
        battery_planner: BatteryPlanner = hass.data[DOMAIN]
        await battery_planner.reschedule(battery_soc)

    hass.services.async_register(DOMAIN, "reschedule", service_call_reschedule)

    return await _dry_setup(hass, config)

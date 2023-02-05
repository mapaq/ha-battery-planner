"""Battery Planner main class"""

import logging
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import EVENT_NEW_DATA
from .charge_schedule import ChargeSchedule

_LOGGER = logging.getLogger(__name__)


class BatteryPlanner:
    """Main class to handle data and push updates"""

    def __init__(self, hass: HomeAssistant):
        self._hass = hass
        self._last_tick = None
        self._active_schedule = None

    async def reschedule(self, battery_state_of_charge: float = None) -> None:
        """Get future prices and create new schedule"""
        _LOGGER.debug(
            "Rescheduling battery, battery state of charge = %s",
            battery_state_of_charge,
        )
        await self._reschedule()

    async def _reschedule(self) -> None:
        _LOGGER.debug("calling _reschedule")
        await self.get_active_schedule(refresh=True)

    async def get_active_schedule(self, refresh: bool = False) -> ChargeSchedule:
        """Get the currently active schedule from API"""
        if self._active_schedule is None or refresh is True:
            self._active_schedule = await self._get_active_schedule()
        return self._active_schedule

    async def _get_active_schedule(self) -> ChargeSchedule:
        schedule = ChargeSchedule()
        schedule.add(datetime.now(), -1000, 1.75)
        schedule.add(datetime.now().replace(hour=1), 1000, 2.75)
        response = schedule
        if response is not None:
            async_dispatcher_send(self._hass, EVENT_NEW_DATA)
        else:
            _LOGGER.error("Could not fetch battery charge schedule")
        return response

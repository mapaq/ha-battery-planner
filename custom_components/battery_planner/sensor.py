"""Sensor to hold the schedule data for Battery Planner"""

import logging
from datetime import datetime

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant, Config
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import POWER_WATT

from .battery_planner import BatteryPlanner
from .charge_schedule import ChargeSchedule
from .const import DOMAIN, EVENT_NEW_DATA

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional("unique_id", default="battery_schedule"): cv.string,
        vol.Optional("friendly_name", default="Battery Charge Schedule"): cv.string,
        vol.Optional("currency", default="SEK"): cv.string,
        vol.Optional("power_unit", default=POWER_WATT): cv.string,
    }
)


def _dry_setup(hass: HomeAssistant, config: Config, add_devices):
    """Setup the platform using yaml"""
    _LOGGER.debug("Setting up Battery Schedule Sensor with config %r", config)
    sensor = BatteryScheduleSensor(
        unique_id=config.get("unique_id"),
        friendly_name=config.get("friendly_name"),
        currency=config.get("currency"),
        power_unit=config.get("power_unit"),
        battery_planner=hass.data[DOMAIN],
        hass=hass,
    )
    add_devices([sensor])


async def async_setup_platform(
    hass: HomeAssistant, config: Config, add_devices, discovery_info=None
) -> None:
    """Setup the sensor from yaml settings"""
    _LOGGER.debug("Setup the sensor from yaml")
    _dry_setup(hass, config, add_devices)
    return True


class BatteryScheduleSensor(SensorEntity):
    """Sensor data"""

    _unique_id: str = None
    _friendly_name: str = None
    _currency: str = None
    _power_unit: str = None
    _battery_planner: BatteryPlanner = None
    _hass: HomeAssistant = None

    _schedule: ChargeSchedule = None
    _expected_yield: float = None

    def __init__(
        self,
        unique_id,
        friendly_name,
        currency,
        power_unit,
        battery_planner,
        hass,
    ) -> None:
        self._unique_id = unique_id
        self._friendly_name = friendly_name
        self._currency = currency
        self._power_unit = power_unit
        self._battery_planner = battery_planner
        self._hass = hass

        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = power_unit

    @property
    def name(self) -> str:
        return self._friendly_name

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        # TODO: Probably needs to poll, or create a coordinator
        return False

    @property
    def icon(self) -> str:
        return "mdi:battery-charging"

    @property
    def unit(self) -> str:
        """Unit"""
        return self._power_unit

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def device_info(self) -> dict[str:object]:
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": DOMAIN,
        }

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        return {
            "currency": self._currency,
            "schedule": str(self._schedule),
            "expected_yield": self._expected_yield,
        }

    async def _update(self) -> None:
        """Callback to update the schedule sensor"""
        _LOGGER.debug("_update")
        self._schedule = await self._battery_planner.get_active_schedule()
        self._attr_native_value = self._schedule.get_power(datetime.now())
        self._expected_yield = self._schedule.get_expected_yield()
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Connect to dispatcher listening for entity data notifications."""
        await super().async_added_to_hass()
        _LOGGER.debug("called async_added_to_hass %s", self.name)
        async_dispatcher_connect(self._hass, EVENT_NEW_DATA, self._update)
        await self._update()

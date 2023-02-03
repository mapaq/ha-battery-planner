"""Sensor to hold the schedule data for Battery Planner"""
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.dispatcher import async_dispatcher_connect

# Import sensor entity and classes.
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)

from . import DOMAIN, EVENT_NEW_DATA

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional("unique_id", default="battery_schedule"): cv.string,
        vol.Optional("friendly_name", default="Battery Schedule"): cv.string,
        vol.Optional("currency", default="SEK"): cv.string,
        vol.Optional("energy_unit", default="kWh"): cv.string,
    }
)


def _dry_setup(hass, config, add_devices):
    """Setup the platform using yaml"""
    _LOGGER.debug("Setting up Battery Schedule Sensor")
    _LOGGER.debug("Dumping config %r", config)
    unique_id = config.get("unique_id")
    friendly_name = config.get("friendly_name")
    currency = config.get("currency")
    energy_unit = config.get("energy_unit")
    battery_scheduler = hass.data[DOMAIN]
    sensor = BatteryScheduleSensor(
        unique_id,
        friendly_name,
        currency,
        energy_unit,
        battery_scheduler,
        hass,
    )
    add_devices([sensor])


async def async_setup_platform(hass, config, add_devices, discovery_info=None) -> None:
    """Setup platform"""
    _dry_setup(hass, config, add_devices)
    return True


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform for the ui"""
    config = config_entry.data
    _dry_setup(hass, config, async_add_devices)
    return True


class BatteryScheduleSensor(SensorEntity):
    """Sensor data"""

    # FIXME: Change device class and state class
    _attr_device_class = SensorDeviceClass.MONETARY
    # _attr_state_class = SensorStateClass.MEASUREMENT
    # https://www.home-assistant.io/integrations/sensor/

    def __init__(
        self,
        unique_id,
        friendly_name,
        currency,
        energy_unit,
        battery_planner,
        hass,
    ) -> None:
        self._unique_id = unique_id
        self._friendly_name = friendly_name
        self._currency = currency
        self._energy_unit = energy_unit
        self._battery_planner = battery_planner
        self._hass = hass
        self._attr_force_update = True

        # Holds the data for today and tomorrow
        self._schedule_today = None
        self._schedule_tomorrow = None

        # Values for the day
        self._charge_cost = None
        self._discharge_earnings = None
        self._arbitrage_return = None

        # To control the updates.
        self._last_tick = None

    @property
    def name(self) -> str:
        return self._unique_id

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
        return self._energy_unit

    @property
    def unit_of_measurement(self) -> str:  # FIXME
        """Return the unit of measurement this sensor expresses itself in."""
        return "%s/%s" % (self._currency, self._energy_unit)

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": DOMAIN,
        }

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "currency": self._currency,
            "unit": self._energy_unit,
        }

    async def _update(self) -> None:
        """Callback to update the schedule sensor"""
        _LOGGER.debug("_update")
        self._attr_native_value = await self._battery_planner.get_active_schedule()
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        await super().async_added_to_hass()
        _LOGGER.debug("called async_added_to_hass %s", self.name)
        async_dispatcher_connect(self._hass, EVENT_NEW_DATA, self._update)
        await self._update()

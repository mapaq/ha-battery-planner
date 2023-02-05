"""Charge Plan"""

import logging
from datetime import datetime, time

_LOGGER = logging.getLogger(__name__)


class ChargePlan:
    """Data class to hold power and price information for each hour"""

    KEY_POWER = "power"
    KEY_PRICE = "price"

    _schedule: dict[str, dict[str : int | float]] = None

    def __init__(self):
        self._schedule = {}

    def __repr__(self):
        return str(self._schedule)

    def __str__(self):
        readable_entry = {}
        for hour, entry in self._schedule.items():
            readable_entry[hour] = entry
        return str(readable_entry)

    def add(self, hour: datetime, power: int, price: float = None) -> None:
        """Add a new hour to the charge plan"""
        entry = {}
        entry[self.KEY_POWER] = power
        entry[self.KEY_PRICE] = price
        self._schedule[hour_iso_string(hour)] = entry

    def get(self, hour: datetime) -> dict[str : int | float]:
        """Get power and price for the hour in a datetime object"""
        hour = hour_iso_string(hour)
        if hour not in self._schedule:
            _LOGGER.error(
                "Tried to get scheduled power value that is not scheduled for hour %s",
                hour,
            )
            return None
        return self._schedule[hour]

    def get_power(self, hour: datetime) -> int:
        """Get the scheduled power value for the given hour"""
        return self.get(hour)[self.KEY_POWER]

    def get_scheduled_hours(self) -> dict[str, dict[str : int | float]]:
        """Get all scheduled hours"""
        return self._schedule

    def get_expected_yield(self) -> float:
        """Get expected financial yield of the planned charging and discharging"""
        expected_yield = 0
        for entry in self._schedule.values():
            power = entry[self.KEY_POWER]
            price = entry[self.KEY_PRICE]
            # TODO: Make power unit and price/energy unit adjustable by sensor settings in yaml
            expected_yield += (power / 1000) * price
        return expected_yield


def hour_iso_string(hour: datetime) -> str:
    """Get string representation of the hour as ISO format"""
    return datetime.combine(hour.date(), time(hour=hour.hour)).isoformat()

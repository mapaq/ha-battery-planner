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
        readable_entry = []
        for hour, entry in self._schedule.items():
            readable_entry.append(f"{hour}: {entry}")
        return str.join("\n", readable_entry)

    def add(self, hour: datetime, power: int, price: float = None) -> None:
        """Add a new hour to the charge plan
        hour - The hour as a datetime object
        power - (W) Negative value means charge, positive means discharge
        price - The electricity price for the given hour in SEK/kWh or other currency/energy"""
        entry = {}
        entry[self.KEY_POWER] = power
        entry[self.KEY_PRICE] = price
        self._schedule[hour_iso_string(hour)] = entry

    def get(self, hour: datetime) -> dict[str : int | float]:
        """Get power and price for the hour in a datetime object"""
        hour_iso = hour_iso_string(hour)
        if hour_iso not in self._schedule:
            _LOGGER.warning(
                "Tried to get value for hour (%s) that is not scheduled. "
                "Returning 0 power and 0.0 price",
                hour_iso,
            )
            entry = {}
            entry[self.KEY_POWER] = 0
            entry[self.KEY_PRICE] = 0.0
            return entry
        return self._schedule[hour_iso]

    def get_power_for_hour(self, hour: datetime) -> int:
        """Get the scheduled power value for the given hour"""
        return self.get(hour)[self.KEY_POWER]

    def scheduled_hours(self) -> dict[str, dict[str : int | float]]:
        """Get all scheduled hours"""
        return self._schedule

    def expected_yield(self) -> float:
        """Get expected financial yield of the planned charging and discharging"""
        expected_yield = 0
        for entry in self._schedule.values():
            power = entry[self.KEY_POWER]
            price = entry[self.KEY_PRICE]
            if price is None:
                # Price might be None when plan is fetched from inverter
                # -> Return None since the price is not valid
                return None
            # TODO: Make power unit and price/energy unit adjustable by sensor settings in yaml
            expected_yield += (power / 1000) * price
        return expected_yield

    def is_empty_plan(self) -> bool:
        """Return True if all power levels for the charge plan is 0"""
        for entry in self._schedule.values():
            power = entry[self.KEY_POWER]
            if power != 0:
                return False
        return True


def hour_iso_string(hour: datetime) -> str:
    """Get string representation of the hour as ISO format"""
    return datetime.combine(hour.date(), time(hour=hour.hour)).isoformat()

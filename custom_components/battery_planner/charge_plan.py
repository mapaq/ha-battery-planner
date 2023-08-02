"""Charge Plan"""

import logging
from datetime import datetime, time

from .charge_hour import ChargeHour

_LOGGER = logging.getLogger(__name__)


class ChargePlan:
    """Data class to hold power and price information for each hour"""

    KEY_POWER = "power"
    KEY_PRICE = "price"

    _schedule: dict[str, ChargeHour]

    def __init__(self):
        self._schedule = {}

    def __repr__(self):
        return str(self._schedule)

    def __str__(self):
        readable_entry = []
        for hour, charge_hour in self._schedule.items():
            readable_entry.append(f"{hour}: {charge_hour}")
        return str.join("\n", readable_entry)

    def add_charge_hour(self, charge_hour: ChargeHour) -> None:
        """Add a new hour from a ChargeHour object"""
        self._schedule[hour_iso_string(charge_hour.get_hour_dt())] = charge_hour.clone()

    def is_scheduled(self, hour: datetime) -> bool:
        """Check if the hour is in the plan"""
        return hour_iso_string(hour) in self._schedule

    def get(self, hour: datetime) -> ChargeHour:
        """Get ChargeHour object"""
        hour_iso = hour_iso_string(hour)
        if hour_iso not in self._schedule:
            _LOGGER.warning(
                "Tried to get value for hour (%s) that is not scheduled. "
                "Returning 0 power and 0.0 price",
                hour_iso,
            )
            return ChargeHour(hour.hour, 0.0, 0.0, 0)
        return self._schedule[hour_iso]

    def get_by_index(self, hour: int) -> ChargeHour:
        """Get charge_hour by index"""
        for charge_hour in self._schedule.values():
            if charge_hour.get_hour() == hour:
                return charge_hour
        raise IndexError(f"Hour with index {hour} not found")

    def get_power(self, hour: datetime) -> int:
        """Get the scheduled power value for the given hour
        hour - The hour as a datetime object
        Return power (W) Negative value is charge (consuming), positive is discharge (producing)
        """
        return int(self.get(hour).get_power_watts())

    def set_power(self, hour: datetime, power: int):
        """Set power value for the given hour
        hour - The hour as a datetime object
        power - (W) Negative value means charge (consuming), positive means discharge (producing)
        """
        self.get(hour).set_power_watts(power)

    def get_price(self, hour: datetime) -> float:
        """Get the price/kWh for the given hour"""
        return self.get(hour).get_active_price()

    def set_price(self, hour: datetime, price: float):
        """Set the price/kWh for the given hour"""
        # TODO: Change to two separate methods? Check if it must be used.
        if self.get(hour).get_power_watts() <= 0:
            self.get(hour).set_import_price(price)
        else:
            self.get(hour).set_export_price(price)

    def scheduled_hours(self) -> dict[str, ChargeHour]:
        """Get all scheduled hours"""
        return self._schedule

    def expected_yield(self) -> float:
        """Get expected financial yield of the planned charging and discharging"""
        expected_yield = 0
        for charge_hour in self._schedule.values():
            power_kw = charge_hour.get_power_watts() / 1000
            price = charge_hour.get_active_price()
            if price is None:
                # Price might be None when plan is fetched from inverter
                # -> Return 0.0
                return 0.0
            expected_yield = round(expected_yield + (power_kw * price), 2)
        return expected_yield

    def get_average_charging_price(self) -> float:
        """Get the average charging price in currency/kWh"""
        energy_added = 0
        total_charging_price = 0
        for charge_hour in self._schedule.values():
            power_watts = charge_hour.get_power_watts()
            price_per_kwh = charge_hour.get_active_price()
            if power_watts < 0:
                power_watts = power_watts * -1
                energy_added += power_watts
                total_charging_price += (power_watts / 1000) * price_per_kwh

        if energy_added > 0:
            return total_charging_price / (energy_added / 1000)
        return 0

    def is_empty_plan(self) -> bool:
        """Return True if all power levels for the charge plan is 0"""
        for charge_hour in self._schedule.values():
            if charge_hour.get_power_watts() != 0:
                return False
        return True

    def clone(self):
        """Create a new object as a clone of this instance"""
        cloned_charge_plan = ChargePlan()
        for charge_hour in self._schedule.values():
            cloned_charge_plan.add_charge_hour(charge_hour.clone())
        return cloned_charge_plan


def hour_iso_string(hour: datetime) -> str:
    """Get string representation of the hour as ISO format"""
    return datetime.combine(hour.date(), time(hour=hour.hour)).isoformat()

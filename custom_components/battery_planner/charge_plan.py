"""Charge Plan"""

import logging
from datetime import datetime, time

from .charge_hour import ChargeHour

_LOGGER = logging.getLogger(__name__)


class ChargePlan:
    """Data class to hold power and price information for each hour"""

    KEY_POWER = "power"
    KEY_PRICE = "price"

    # The key is an hour represented as datetime in ISO string format
    # {"2023-08-20T00:00:00": ChargeHour object}
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
        self._schedule[hour_iso_string(charge_hour.get_time())] = charge_hour.clone()
        self._schedule = dict(
            sorted(self._schedule.items(), key=lambda d: d[1].get_time())
        )

    def pop(self, index: int = 0) -> ChargeHour:
        """Remove item from plan based on index value"""
        return self._schedule.pop(self.get_hours_list()[index].hour_iso_string())

    def is_scheduled(self, hour: datetime) -> bool:
        """Check if the hour is in the plan"""
        return hour_iso_string(hour) in self._schedule

    def get(self, hour_iso: str) -> ChargeHour:
        """Get ChargeHour object"""
        return self._schedule[hour_iso]

    def get_by_dt(self, hour: datetime) -> ChargeHour:
        """Get ChargeHour object by datetime"""
        hour_iso = hour_iso_string(hour)
        if hour_iso not in self._schedule:
            _LOGGER.warning(
                "Tried to get value for hour (%s) that is not scheduled. "
                "Returning 0 power and 0.0 price",
                hour_iso,
            )
            return ChargeHour(hour.hour, 0.0, 0.0, 0)
        return self._schedule[hour_iso]

    def get_by_index(self, index: int) -> ChargeHour:
        """Get charge_hour by index"""
        try:
            return self.get_hours_list()[index]
        except IndexError as error:
            raise IndexError(f"Hour with index {index} not found") from error

    def get_next_after(self, charge_hour: ChargeHour) -> ChargeHour | None:
        """Get the next hour after the provided one"""
        try:
            return self.get_by_index(self.index_of(charge_hour) + 1)
        except IndexError:
            return None

    def index_of(self, charge_hour: ChargeHour) -> int:
        """Get the index of a charge_hour"""
        hour_in_list = self.get_by_dt(charge_hour.get_time())
        return self.get_hours_list().index(hour_in_list)

    def get_last(self) -> ChargeHour:
        """Get the last hour in charge plan"""
        sorted_by_time = sorted(
            self._schedule.values(), key=lambda hour: hour.get_time()
        )
        return sorted_by_time[-1]

    def get_first_active_hour(self) -> ChargeHour | None:
        """Return the first hour that has been scheduled with a power level"""
        for hour in self.get_hours_list():
            if hour.get_power() != 0:
                return hour
        return None

    def get_power(self, hour: datetime) -> int:
        """Get the scheduled power value for the given hour
        hour - The hour as a datetime object
        Return power (W) Negative value is charge (consuming), positive is discharge (producing)
        """
        return int(self.get_by_dt(hour).get_power())

    def set_power(self, hour: datetime, power: int):
        """Set power value for the given hour
        hour - The hour as a datetime object
        power - (W) Negative value means charge (consuming), positive means discharge (producing)
        """
        self.get_by_dt(hour).set_power(power)

    def get_hours_list(self) -> list[ChargeHour]:
        """Get all scheduled hours as a list"""
        return list(self._schedule.values())

    def get_hours_dict(self) -> dict[str, ChargeHour]:
        """Get all scheduled hours"""
        return self._schedule

    def get_hours_serializeable(
        self,
    ) -> dict[str, dict[str, str | int | float]]:
        """Get all sceduled hours as a serializable object"""
        schedule: dict[str, dict[str, str | int | float]] = {}
        for hour_iso, charge_hour in self._schedule.items():
            charge_hour_dict = charge_hour.to_json()
            try:
                del charge_hour_dict["hour"]
            except KeyError:
                pass
            schedule[hour_iso] = charge_hour_dict
        return schedule

    # TODO: Shall this calculation include the battery average charge cost?
    # It might need to do that if this is to be used by the sensor.
    # The charge_plan should in that case have a battery object with inital values it
    # was created with.
    def expected_yield(self) -> float:
        """Get expected financial yield of the planned charging and discharging"""
        expected_yield = 0
        for charge_hour in self._schedule.values():
            power_kw = charge_hour.get_power() / 1000
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
            power_watts = charge_hour.get_power()
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
            if charge_hour.get_power() != 0:
                return False
        return True

    def clone(self):
        """Create a new object as a clone of this instance"""
        cloned_charge_plan = ChargePlan()
        for charge_hour in self._schedule.values():
            cloned_charge_plan.add_charge_hour(charge_hour.clone())
        return cloned_charge_plan

    def len(self):
        """Get the length of the charge plan, i.e. the number of ChargeHours"""
        return len(self.get_hours_dict())


def hour_iso_string(hour: datetime) -> str:
    """Get string representation of the hour as ISO format"""
    return datetime.combine(hour.date(), time(hour=hour.hour)).isoformat()

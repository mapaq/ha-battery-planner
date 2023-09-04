"""Fictive battery to store calculated charge levels"""

import logging
import math

from .charge_hour import ChargeHour

_LOGGER = logging.getLogger(__name__)


class Battery:
    """Data class to hold information and charge level of the fictive battery

    capacity - (Wh) Total energy capacity of the battery\n
    _max_charge_power - (W) Maximum allowed charge power\n
    _max_discharge_power - (W) Maximum allowed discharge power\n
    _lower_soc_limit - (%) Minimum allowed state of charge, e.g. 5% = 0.05\n
    _upper_soc_limit - (%) Maximum allowed state of charge, e.g. 5% = 0.95"""

    _max_charge_power: int
    _max_discharge_power: int
    _capacity: int
    _upper_soc_limit: float
    _lower_soc_limit: float
    _soc: float
    _energy_watthours: int
    _average_charge_cost_per_kwh: float

    def __init__(
        self,
        capacity: int,
        max_charge_power: int,
        max_discharge_power: int,
        upper_soc_limit: int,
        lower_soc_limit: int,
    ):
        self._capacity = capacity
        self._max_charge_power = max_charge_power
        self._max_discharge_power = max_discharge_power
        self._upper_soc_limit = upper_soc_limit / 100
        self._lower_soc_limit = lower_soc_limit / 100
        self.set_soc(0.0)
        self._average_charge_cost_per_kwh = 0.0

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        readable = {}
        readable["Capacity"] = self._capacity
        readable["Upper SoC limit"] = self._upper_soc_limit
        readable["Lower SoC limit"] = self._lower_soc_limit
        readable["Max charge power"] = self._max_charge_power
        readable["Max discharge power"] = self._max_discharge_power
        readable["Energy level"] = self._energy_watthours
        return str(readable)

    def set_soc(self, soc: float):
        """Set state of charge and calculate the energy level of the battery
        soc - (%) The current state of charge of the battery, e.g. 100% = 1.0"""
        self._soc = soc
        self._energy_watthours = int(self._capacity * soc)

    def set_max_charge_power(self, power: int) -> None:
        """Set the max allowed charge power (W)"""
        self._max_charge_power = power

    def get_max_charge_power(self) -> int:
        """Get the max allowed charge power (W)"""
        return self._max_charge_power

    def set_max_discharge_power(self, power: int) -> None:
        """Set the max allowed discharge power (W)"""
        self._max_discharge_power = power

    def get_max_discharge_power(self) -> int:
        """Get the max allowed discharge power (W)"""
        return self._max_discharge_power

    def get_capacity(self) -> int:
        """Get total battery energy storage capacity (Wh)"""
        return self._capacity

    def get_available_capacity(self) -> int:
        """Get the available capacity after adjusting for lower and upper soc limit"""
        unavailable_capacity = (
            1 - self._upper_soc_limit + self._lower_soc_limit
        ) * self._capacity
        return int(self._capacity - unavailable_capacity)

    def set_energy(self, energy: int):
        """Set energy level"""
        self._energy_watthours = energy

    def get_energy(self) -> int:
        """Get stored energy amount (Wh)"""
        return self._energy_watthours

    def set_average_charge_cost(self, cost: float) -> None:
        """Set the average charge cost"""
        self._average_charge_cost_per_kwh = cost

    def get_average_charge_cost(self) -> float:
        """Get the average charge cost"""
        return self._average_charge_cost_per_kwh

    def min_energy_limit(self) -> int:
        """Minimum allowed energy level based on capacity and minimum SoC limit (Wh)"""
        return int(self._capacity * self._lower_soc_limit)

    def is_full(self) -> bool:
        """Return True if the battery is fully charged"""
        return self._energy_watthours >= self._capacity * self._upper_soc_limit

    def is_empty(self) -> bool:
        """Return True if the battery is below or equal to soc limit"""
        return self._energy_watthours <= self._capacity * self._lower_soc_limit

    def add_energy(self, energy: int) -> None:
        """Change the battery energy level (Wh)"""
        self._energy_watthours += energy
        self._energy_watthours = max(self._energy_watthours, self.min_energy_limit())

    def charge_max_power_for_one_hour(self, charge_hour: ChargeHour) -> int:
        """Use max allowed charge level to set the charge level for the charge hour

        Return the power level to charge the battery"""
        return self.charge(self._max_charge_power, charge_hour)

    def charge(self, max_charge_power: int, charge_hour: ChargeHour) -> int:
        """Increase stored energy of the fictive battery

        Return the power level to charge the battery"""
        charge_power = min(
            self.remaining_energy_below_upper_soc_limit(), max_charge_power
        )
        charge_hour.set_power_watts(int(-charge_power))
        self.update_average_charge_cost(charge_hour)
        self._energy_watthours += charge_power
        return int(-charge_power)

    def discharge_max_power_for_one_hour(self, charge_hour: ChargeHour) -> int:
        """Use max allowed discharge level

        Return the power level to discharge the battery"""
        return self.discharge(self._max_discharge_power, charge_hour)

    def discharge(self, max_discharge_power: int, charge_hour: ChargeHour) -> int:
        """Decrease stored energy of the fictive battery

        Return the power level to discharge the battery"""
        discharge_power = min(
            self.remaining_energy_above_lower_soc_limit(), max_discharge_power
        )
        charge_hour.set_power_watts(int(discharge_power))
        self._energy_watthours -= discharge_power
        return int(discharge_power)

    def remaining_energy_below_upper_soc_limit(self):
        """The remaining amount of energy below upper soc limit"""
        return max(
            0, int((self._capacity * self._upper_soc_limit) - self._energy_watthours)
        )

    def remaining_energy_above_lower_soc_limit(self):
        """The remaining amount of energy above lower soc limit"""
        return max(
            0, int(self._energy_watthours - (self._capacity * self._lower_soc_limit))
        )

    def calculate_new_average_charge_cost(self, charge_hour: ChargeHour) -> float:
        """Calculate new average charge cost for the energy stored in the battery"""
        new_energy_watthours = charge_hour.get_power_watts() * -1
        new_charge_cost = new_energy_watthours * charge_hour.get_active_price()
        previous_charge_cost = (
            self._average_charge_cost_per_kwh * self._energy_watthours
        )
        new_average_charge_cost = (previous_charge_cost + new_charge_cost) / (
            self._energy_watthours + new_energy_watthours
        )
        return new_average_charge_cost

    def update_average_charge_cost(self, charge_hour: ChargeHour) -> None:
        """Update the average charge cost with the new hour"""
        self._average_charge_cost_per_kwh = self.calculate_new_average_charge_cost(
            charge_hour
        )

    def needed_hours_to_deplete(self) -> int:
        """Calculate the number of needed hours to fully discharge the battery to lower soc limit"""
        return math.ceil(self.get_available_capacity() / self.get_max_discharge_power())

    def needed_hours_to_fill(self) -> int:
        """Calculate the number of needed hours to fully charge the battery to upper soc limit"""
        return math.ceil(self.get_available_capacity() / self.get_max_charge_power())

    def clone(self):
        """Create a new object as a clone of this instance"""
        cloned_battery = Battery(
            capacity=self._capacity,
            max_charge_power=self._max_charge_power,
            max_discharge_power=self._max_discharge_power,
            upper_soc_limit=int(self._upper_soc_limit * 100),
            lower_soc_limit=int(self._lower_soc_limit * 100),
        )
        cloned_battery.set_energy(self._energy_watthours)
        cloned_battery.set_average_charge_cost(self._average_charge_cost_per_kwh)
        return cloned_battery

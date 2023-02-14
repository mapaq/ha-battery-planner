"""Fictive battery to store calculated charge levels"""

import logging

_LOGGER = logging.getLogger(__name__)


class Battery:
    """Data class to hold information and charge level of the fictive battery

    capacity - (Wh) Total energy capacity of the battery
    max_charge_power - (W) Maximum allowed charge power
    max_discharge_power - (W) Maximum allowed discharge power
    soc_limit - (%) Minimum allowed state of charge, e.g. 5% = 0.05"""

    _max_charge_power: int
    _max_discharge_power: int

    capacity: int
    _soc_limit: float
    _soc: float
    energy: int

    def __init__(
        self,
        capacity: int,
        max_charge_power: int,
        max_discharge_power: int,
        soc_limit: float,
    ):
        self.capacity = capacity
        self._max_charge_power = max_charge_power
        self._max_discharge_power = max_discharge_power
        self._soc_limit = soc_limit
        self.set_soc(0.0)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        readable = {}
        readable["Capacity"] = self.capacity
        readable["SoC limit"] = self._soc_limit
        readable["Max charge power"] = self._max_charge_power
        readable["Max discharge power"] = self._max_discharge_power
        readable["Energy level"] = self.energy
        return str(readable)

    def set_soc(self, soc: float):
        """Set state of charge and calculate the energy level of the battery
        soc - (%) The current state of charge of the battery, e.g. 100% = 1.0"""
        self._soc = soc
        self.energy = int(self.capacity * soc)

    def min_energy_limit(self) -> int:
        """Minimum allowed energy level based on capacity and minimum SoC limit"""
        return int(self.capacity * self._soc_limit)

    def is_full(self) -> bool:
        """Return True if the battery is fully charged"""
        return self.energy == self.capacity

    def is_empty(self) -> bool:
        """Return True if the battery is below or equal to soc limit"""
        return self.energy <= self.capacity * self._soc_limit

    def add_energy(self, energy: int) -> None:
        """Change the battery energy level"""
        self.energy += energy
        self.energy = max(self.energy, self.min_energy_limit())

    def charge_max(self) -> int:
        """Use max allowed charge level"""
        return self.charge(self._max_charge_power)

    def charge(self, max_charge_power: int) -> int:
        """Increase stored energy of the fictive battery"""
        charge_power = min(self.capacity - self.energy, max_charge_power)
        self.energy += charge_power

        if self.energy == self.capacity:
            charge_power += self._extra_power_to_fully_charge_or_deplete_the_battery(
                max_charge_power
            )

        return int(-charge_power)

    def discharge_max(self) -> int:
        """Use max allowed discharge level"""
        return self.discharge(self._max_discharge_power)

    def discharge(self, max_discharge_power: int) -> int:
        """Decrease stored energy of the fictive battery"""
        discharge_power = min(
            self.remaining_energy_above_soc_limit(), max_discharge_power
        )
        self.energy -= discharge_power

        if self.remaining_energy_above_soc_limit() == 0:
            discharge_power += self._extra_power_to_fully_charge_or_deplete_the_battery(
                max_discharge_power
            )

        return int(discharge_power)

    def remaining_energy_above_soc_limit(self):
        """The remaining amount of energy above soc limit energy level"""
        return max(0, int(self.energy - self.capacity * self._soc_limit))

    def _extra_power_to_fully_charge_or_deplete_the_battery(
        self, max_power: int
    ) -> int:
        """When charging and discharging there might be some minor difference between
        the planned charging and the actual energy charged. Therefore we add some extra
        power to help reach 100% when chargin or the SoC limit when discharging"""
        return min(int(self.capacity * 0.05), max_power)

"""ChargePlan tests module"""

from datetime import datetime, time

import pytest

from custom_components.battery_planner.charge_plan import ChargePlan, hour_iso_string
from custom_components.battery_planner.charge_hour import ChargeHour
from .fixtures import *


class TestChargePlan:
    def test_expected_yield(self):
        charge_plan = ChargePlan()
        charge_plan.add_charge_hour(ChargeHour(0, 97.58, 39.1, -1000))
        charge_plan.add_charge_hour(ChargeHour(1, 165.69, 93.59, 0))
        charge_plan.add_charge_hour(ChargeHour(2, 186.5, 110.24, 1000))
        charge_plan.add_charge_hour(ChargeHour(3, 183.57, 107.9, 0))
        charge_plan.add_charge_hour(ChargeHour(4, 80.1, 25.12, 0))
        charge_plan.add_charge_hour(ChargeHour(5, 71.98, 18.62, -1000))
        charge_plan.add_charge_hour(ChargeHour(6, 97.79, 39.27, 0))
        charge_plan.add_charge_hour(ChargeHour(7, 166.61, 94.33, 1000))
        charge_plan.add_charge_hour(ChargeHour(8, 93.67, 35.98, -1000))
        charge_plan.add_charge_hour(ChargeHour(9, 94.09, 36.31, 0))
        charge_plan.add_charge_hour(ChargeHour(10, 205.3, 125.28, 1000))
        assert charge_plan.expected_yield() == 66.62

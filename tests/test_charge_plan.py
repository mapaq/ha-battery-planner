"""ChargePlan tests module"""

from datetime import datetime, time

import pytest

from custom_components.battery_planner.charge_plan import ChargePlan
from custom_components.battery_planner.charge_hour import ChargeHour
from .fixtures import *
from .test_data import *


class TestChargePlan:
    @pytest.mark.parametrize(
        "data",
        [
            short_price_series_with_3_cycles,
            short_price_series_with_consecutive_charge_battery_two_kw_three_kwh,
        ],
    )
    def test_expected_yield(self, data):
        charge_plan = ChargePlan()
        for i, power in enumerate(data["powers"]):
            charge_plan.add_charge_hour(
                ChargeHour(i, data["import"][i], data["export"][i], power)
            )
        assert charge_plan.expected_yield() == data["yield"]

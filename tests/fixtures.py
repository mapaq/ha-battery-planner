"""Test fixtures"""

import pytest

from datetime import datetime, time

from custom_components.battery_planner.battery import Battery
from custom_components.battery_planner.planner import Planner


@pytest.fixture
def battery_one_kw_one_kwh() -> Battery:
    return Battery(
        capacity=1000,
        max_charge_power=1000,
        max_discharge_power=1000,
        upper_soc_limit=100,
        lower_soc_limit=0,
    )


@pytest.fixture
def battery_one_kw_two_kwh() -> Battery:
    return Battery(
        capacity=2000,
        max_charge_power=1000,
        max_discharge_power=1000,
        upper_soc_limit=100,
        lower_soc_limit=0,
    )


@pytest.fixture
def battery_two_kw_three_kwh() -> Battery:
    return Battery(
        capacity=3000,
        max_charge_power=2000,
        max_discharge_power=2000,
        upper_soc_limit=100,
        lower_soc_limit=0,
    )


@pytest.fixture
def hour_dt(hour: int) -> datetime:
    return datetime.combine(datetime.now().date(), time(hour=hour))


@pytest.fixture
def planner() -> Planner:
    return Planner(cheap_import_price_limit=0)

"""Planner tests module"""

from datetime import datetime, time

import pytest

from custom_components.battery_planner.planner import Planner
from custom_components.battery_planner.battery import Battery
from custom_components.battery_planner.charge_plan import ChargePlan, hour_iso_string
from .fixtures import *
from .test_data import *


class TestPlanner:
    def test_create_price_arbitrage_plan_returns_a_charge_plan(
        self, planner: Planner, battery_one_kw_one_kwh: Battery
    ):
        charge_plan: ChargePlan = planner.create_price_arbitrage_plan(
            battery=battery_one_kw_one_kwh,
            import_prices=[1.0, 2.0],
            export_prices=[1.0, 2.0],
        )
        assert isinstance(charge_plan, ChargePlan) is True

    @pytest.mark.parametrize("hour", [0])
    def test_first_hour_is_0000(
        self, planner: Planner, battery_one_kw_one_kwh: Battery, hour_dt: datetime
    ):
        charge_plan: ChargePlan = planner.create_price_arbitrage_plan(
            battery=battery_one_kw_one_kwh,
            import_prices=[1.0, 2.0],
            export_prices=[1.0, 2.0],
        )
        assert charge_plan.is_scheduled(hour_dt)

    @pytest.mark.parametrize("hour", [1])
    def test_charge_at_0100(
        self, planner: Planner, battery_one_kw_one_kwh: Battery, hour_dt: datetime
    ):
        charge_plan: ChargePlan = planner.create_price_arbitrage_plan(
            battery=battery_one_kw_one_kwh,
            import_prices=[3.0, 2.0, 4.0],
            export_prices=[1.0, 1.0, 3.0],
        )
        assert charge_plan.get_by_dt(hour_dt).get_power_watts() == -1000

    def test_charge_at_0300(self, planner: Planner, battery_one_kw_one_kwh: Battery):
        charge_plan = planner.create_price_arbitrage_plan(
            battery=battery_one_kw_one_kwh,
            import_prices=[3.0, 2.0, 4.0, 1.0, 5.0],
            export_prices=[1.0, 1.0, 3.0, 1.0, 4.0],
        )
        assert (
            charge_plan.get_by_dt(
                datetime.combine(datetime.now().date(), time(hour=3))
            ).get_power_watts()
            == -1000
        )

    @pytest.mark.parametrize(
        "data",
        [
            short_price_series_with_1_cycle,
            short_price_series_with_2_cycles,
            short_price_series_with_3_cycles,
            long_price_series_with_3_cycles,
            long_price_series_with_3_cycles_2,
        ],
    )
    def test_charge_cost(
        self,
        planner: Planner,
        battery_one_kw_one_kwh: Battery,
        data: dict[str, list[float]],
    ):
        charge_plan: ChargePlan = planner.create_price_arbitrage_plan(
            battery_one_kw_one_kwh,
            data["import"],
            data["export"],
        )
        assert charge_plan.expected_yield() == data["yield"], f"\n{charge_plan}"
        if "plan" in data:
            for hour, power in enumerate(data["plan"]):
                assert charge_plan.get_by_index(hour).get_power_watts() == power

    @pytest.mark.parametrize(
        "data",
        [
            short_price_series_with_one_cycle_battery_charged_1,
            short_price_series_with_one_cycle_battery_charged_2,
            short_price_series_with_one_cycle_battery_charged_3,
        ],
    )
    def test_charge_cost_for_already_charged_battery(
        self,
        planner: Planner,
        battery_one_kw_one_kwh: Battery,
        data: dict[str, list[float]],
    ):
        battery_one_kw_one_kwh.set_energy(int(data["battery_energy"][0]))
        battery_one_kw_one_kwh.set_average_charge_cost(data["average_charge_cost"][0])
        charge_plan: ChargePlan = planner.create_price_arbitrage_plan(
            battery_one_kw_one_kwh,
            data["import"],
            data["export"],
        )
        assert (
            charge_plan.expected_yield()
            - battery_one_kw_one_kwh.get_average_charge_cost()
            == data["yield"][0]
        ), f"\n{charge_plan}"
        if "plan" in data:
            for hour, power in enumerate(data["plan"]):
                assert charge_plan.get_by_index(hour).get_power_watts() == power

    @pytest.mark.parametrize(
        "data",
        [short_price_series_with_consecutive_charge],
    )
    def test_consecutive_charge(
        self, planner: Planner, battery_one_kw_two_kwh: Battery, data
    ):
        charge_plan: ChargePlan = planner.create_price_arbitrage_plan(
            battery_one_kw_two_kwh,
            data["import"],
            data["export"],
        )
        assert charge_plan.expected_yield() == data["yield"], f"\n{charge_plan}"
        if "plan" in data:
            for hour, power in enumerate(data["plan"]):
                assert charge_plan.get_by_index(hour).get_power_watts() == power

    @pytest.mark.parametrize(
        "data",
        [short_price_series_with_consecutive_charge_battery_two_kw_three_kwh],
    )
    def test_consecutive_charge_with_different_power(
        self, planner: Planner, battery_two_kw_three_kwh: Battery, data
    ):
        charge_plan: ChargePlan = planner.create_price_arbitrage_plan(
            battery_two_kw_three_kwh,
            data["import"],
            data["export"],
        )
        assert charge_plan.expected_yield() == data["yield"], f"\n{charge_plan}"
        if "plan" in data:
            for hour, power in enumerate(data["plan"]):
                assert charge_plan.get_by_index(hour).get_power_watts() == power

    @pytest.mark.parametrize(
        "data",
        [
            short_price_series_with_3_cycles_start_at_04,
            long_price_series_start_on_hour_21,
        ],
    )
    def test_ignore_passed_hours(
        self, planner: Planner, battery_one_kw_one_kwh: Battery, data
    ):
        battery: Battery = battery_one_kw_one_kwh
        start_hour = data["start_hour"]
        if "battery" in data:
            batt = data["battery"]
            battery = Battery(
                batt["capacity"],
                batt["max_charge_power"],
                batt["max_discharge_power"],
                batt["upper_soc_limit"],
                batt["lower_soc_limit"],
            )
            battery.set_soc(batt["soc"])
        charge_plan: ChargePlan = planner.create_price_arbitrage_plan(
            battery, data["import"], data["export"], start_hour
        )
        assert charge_plan.expected_yield() == data["yield"], f"\n{charge_plan}"
        assert charge_plan.len() == len(data["plan"])
        assert charge_plan.get_by_index(0).get_time().hour == start_hour
        if "plan" in data:
            for hour, power in enumerate(data["plan"]):
                assert charge_plan.get_by_index(hour).get_power_watts() == power


# Need to pass datetime with "first_hour" to the planner, or simply remove passed hours before
# sending to planner

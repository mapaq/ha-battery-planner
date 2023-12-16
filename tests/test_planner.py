"""Planner tests module"""

from datetime import datetime, time, timedelta
from typing import Any

import pytest

from custom_components.battery_planner.planner import Planner, create_empty_plan
from custom_components.battery_planner.battery import Battery
from custom_components.battery_planner.charge_plan import ChargePlan
from custom_components.battery_planner.charge_hour import ChargeHour
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
        assert charge_plan.get_by_dt(hour_dt).get_power() == -1000

    def test_charge_at_0300(self, planner: Planner, battery_one_kw_one_kwh: Battery):
        charge_plan = planner.create_price_arbitrage_plan(
            battery=battery_one_kw_one_kwh,
            import_prices=[3.0, 2.0, 4.0, 1.0, 5.0],
            export_prices=[1.0, 1.0, 3.0, 1.0, 4.0],
        )
        assert (
            charge_plan.get_by_dt(
                datetime.combine(datetime.now().date(), time(hour=3))
            ).get_power()
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
        verify_plan(data, charge_plan)

    @pytest.mark.parametrize(
        "data",
        [
            short_price_series_with_one_cycle_battery_charged_1,
            short_price_series_with_one_cycle_battery_charged_2,
            short_price_series_with_one_cycle_battery_charged_3,
            short_price_series_with_one_cycle_battery_charged_4,
        ],
    )
    def test_charge_cost_for_already_charged_battery(
        self,
        planner: Planner,
        battery_one_kw_one_kwh: Battery,
        data: dict[str, Any],
    ):
        battery_one_kw_one_kwh.set_energy(int(data["battery_energy"]))
        battery_one_kw_one_kwh.set_average_charge_cost(
            float(data["average_charge_cost"])
        )
        charge_plan: ChargePlan = planner.create_price_arbitrage_plan(
            battery_one_kw_one_kwh,
            data["import"],
            data["export"],
        )
        data["yield"] = data["yield"] + data["average_charge_cost"]
        verify_plan(data, charge_plan)

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
        verify_plan(data, charge_plan)

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
        verify_plan(data, charge_plan)

    @pytest.mark.parametrize(
        "data",
        [
            short_price_series_with_3_cycles_start_at_04,
            long_price_series_start_on_hour_21,
            long_price_series_start_hour_18_soc_90,
            long_price_series_start_hour_21_soc_10,
            long_price_series_start_hour_17_soc_80,
            long_price_series_start_hour_15_soc_80,
            long_price_series_start_hour_14_soc_90,
        ],
    )
    def test_ignore_passed_hours(self, battery_one_kw_one_kwh: Battery, data):
        battery: Battery = battery_one_kw_one_kwh
        start_hour = int(data["start_hour"])
        cycle_cost = 0
        price_margin = 0
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

            if "average_charge_cost" in data:
                battery.set_average_charge_cost(float(data["average_charge_cost"]))

            if "cycle_cost" in data["battery"]:
                cycle_cost = data["battery"]["cycle_cost"]
        if "price_margin" in data:
            price_margin = data["price_margin"]

        if "charge_plan" in data:
            test_data_charge_plan = create_charge_plan(data["charge_plan"])
            data["yield"] = test_data_charge_plan.expected_yield()
            data["import"] = extract_import_prices(test_data_charge_plan)
            data["export"] = extract_export_prices(test_data_charge_plan)
            data["powers"] = extract_powers(test_data_charge_plan, start_hour)

        planner = Planner(cycle_cost, price_margin, 0)
        charge_plan: ChargePlan = planner.create_price_arbitrage_plan(
            battery, data["import"], data["export"], start_hour
        )
        assert charge_plan.get_by_index(0).get_time().hour == start_hour
        verify_plan(data, charge_plan)

    @pytest.mark.parametrize(
        "data",
        [
            short_price_series_with_low_prices,
        ],
    )
    def test_charge_at_low_price(self, data):
        planner = Planner(0, 0, data["low_price_threshold"])
        batt = data["battery"]
        battery = Battery(
            batt["capacity"],
            batt["max_charge_power"],
            batt["max_discharge_power"],
            batt["upper_soc_limit"],
            batt["lower_soc_limit"],
        )
        battery.set_soc(batt["soc"])
        charge_plan = planner.create_price_arbitrage_plan(
            battery, data["import"], data["export"]
        )
        verify_plan(data, charge_plan)

    def test_create_empty_plan(self):
        charge_plan = create_empty_plan()
        assert charge_plan.is_empty_plan()

    def test_create_empty_plan_returns_plan_of_length_48(self):
        charge_plan = create_empty_plan()
        assert charge_plan.len() == 48

    def test_create_empty_plan_returns_plan_of_length_48_minus_start_hour(self):
        charge_plan = create_empty_plan(5)
        assert charge_plan.len() == 48 - 5

    def test_create_empty_plan_returns_plan_ending_tomorrow_23_00(self):
        charge_plan = create_empty_plan()
        tomorrow = datetime.now() + timedelta(days=1)
        assert charge_plan.get_last().get_time().date() == tomorrow.date()
        assert charge_plan.get_last().get_time().hour == 23

    def test_create_empty_plan_returns_plan_of_same_length_as_price_array(self):
        charge_plan = create_empty_plan(0, [0.0] * 20, [0.0] * 20)
        assert charge_plan.len() == 20

        charge_plan = create_empty_plan(0, [0.0] * 48, [0.0] * 48)
        assert charge_plan.len() == 48

    def test_create_empty_plan_fails_if_price_arrays_are_of_different_lengths(self):
        with pytest.raises(ValueError):
            charge_plan = create_empty_plan(0, [0.0] * 20, [0.0] * 21)


def verify_plan(data, charge_plan: ChargePlan):
    if "powers" in data:
        error_message = f'\nExpected plan:\n{data["powers"]}\nActual plan:\n{extract_powers(charge_plan, 0)}'
        for hour, power in enumerate(data["powers"]):
            assert (
                charge_plan.get_by_index(hour).get_power() == power
            ), f"{error_message}\n\n{charge_plan}"
    assert charge_plan.len() == len(data["powers"]), f"\n{charge_plan}"
    assert charge_plan.expected_yield() == data["yield"], f"\n{charge_plan}"


def create_charge_plan(charge_plan_data: list[dict[str, int | float]]) -> ChargePlan:
    charge_plan = ChargePlan()
    for hour_data in charge_plan_data:
        charge_plan.add_charge_hour(
            ChargeHour(
                hour=int(hour_data["Index"]),
                import_price=float(hour_data["Import"]),
                export_price=float(hour_data["Export"]),
                power=int(hour_data["Power"]),
            )
        )
    return charge_plan


def extract_import_prices(charge_plan: ChargePlan) -> list[float]:
    prices = []
    for h in charge_plan.get_hours_list():
        prices.append(h.get_import_price())
    return prices


def extract_export_prices(charge_plan: ChargePlan) -> list[float]:
    prices = []
    for h in charge_plan.get_hours_list():
        prices.append(h.get_export_price())
    return prices


def extract_powers(charge_plan: ChargePlan, start_hour: int) -> list[int]:
    powers = []
    for h in charge_plan.get_hours_list():
        powers.append(h.get_power())
    return powers[start_hour:]

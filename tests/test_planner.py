"""Planner tests module"""

from datetime import datetime, time

import pytest

from custom_components.battery_planner.planner import Planner
from custom_components.battery_planner.battery import Battery
from custom_components.battery_planner.charge_plan import ChargePlan, hour_iso_string
from .fixtures import *


class TestPlanner:
    def test_create_price_arbitrage_plan_returns_a_charge_plan(
        self, planner: Planner, battery_one_kw_one_kwh: Battery
    ):
        charge_plan = planner.create_price_arbitrage_plan(
            battery=battery_one_kw_one_kwh,
            import_prices=[1.0, 2.0],
            export_prices=[1.0, 2.0],
        )
        assert isinstance(charge_plan, ChargePlan) is True

    @pytest.mark.parametrize("hour", [0])
    def test_first_hour_is_0000(
        self, planner: Planner, battery_one_kw_one_kwh: Battery, hour_dt: datetime
    ):
        charge_plan = planner.create_price_arbitrage_plan(
            battery=battery_one_kw_one_kwh,
            import_prices=[1.0, 2.0],
            export_prices=[1.0, 2.0],
        )
        assert charge_plan.is_scheduled(hour_dt)

    @pytest.mark.parametrize("hour", [1])
    def test_charge_at_0100(
        self, planner: Planner, battery_one_kw_one_kwh: Battery, hour_dt: datetime
    ):
        charge_plan = planner.create_price_arbitrage_plan(
            battery=battery_one_kw_one_kwh,
            import_prices=[3.0, 2.0, 4.0],
            export_prices=[1.0, 1.0, 3.0],
        )
        assert charge_plan.get(hour_dt).get_power_watts() == -1000

    def test_charge_at_0300(self, planner: Planner, battery_one_kw_one_kwh: Battery):
        charge_plan = planner.create_price_arbitrage_plan(
            battery=battery_one_kw_one_kwh,
            import_prices=[3.0, 2.0, 4.0, 1.0, 5.0],
            export_prices=[1.0, 1.0, 3.0, 1.0, 4.0],
        )
        assert (
            charge_plan.get(
                datetime.combine(datetime.now().date(), time(hour=3))
            ).get_power_watts()
            == -1000
        )

    @pytest.mark.parametrize(
        "prices",
        [
            {
                "import": [3.0, 2.0, 4.0, 4.0],
                "export": [1.0, 1.0, 3.0, 1.0],
                "yield": 1.0,
                "plan": [0, -1000, 1000, 0],
            },
            {
                "import": [3.0, 2.0, 4.0, 1.0, 5.0],
                "export": [1.0, 1.0, 3.0, 4.0, 4.0],
                "yield": 4.0,
                "plan": [0, -1000, 1000, -1000, 1000],
            },
            {
                "import": [
                    97.58,  # 1
                    165.69,
                    186.5,  # 1  110.24 - 97.58 = 12.66
                    183.57,
                    80.1,
                    71.98,  # 2
                    97.79,
                    166.61,  # 2  94.33 - 71.98 = 22.35
                    93.67,  # 3
                    94.09,
                    205.3,  # 3  125.28 - 93.67 = 31.61
                ],
                "export": [
                    39.1,  # 1
                    93.59,
                    110.24,  # 1
                    107.9,
                    25.12,
                    18.62,  # 2
                    39.27,
                    94.33,  # 2
                    35.98,  # 3
                    36.31,
                    125.28,  # 3
                ],
                "yield": 66.62,  # 12.66 + 22.35 + 31.61 = 66.62
                "plan": [
                    -1000,  # 1
                    0,
                    1000,  # 1
                    0,
                    0,
                    -1000,  # 2
                    0,
                    1000,  # 2
                    -1000,  # 3
                    0,
                    1000,  # 3
                ],
            },
            # # {
            #     "import": [
            #         194.22,
            #         153.04,
            #         145.39,
            #         162.59,
            #         167.08,
            #         191.09,
            #         212.21,
            #         223.19,
            #         206.66,
            #         194.24,
            #         179.6,
            #         158.94,
            #         141.24,
            #         114.38,
            #         101.75,
            #         97.58,  # 1
            #         107.04,
            #         142.01,
            #         165.69,
            #         186.5,  # 1
            #         183.57,
            #         175.55,
            #         160.64,
            #         101.36,
            #         78.12,
            #         80.1,
            #         71.98,  # 2
            #         75.42,
            #         77.71,
            #         78.49,
            #         88.99,
            #         97.79,
            #         166.61,  # 2
            #         150.12,
            #         126.56,
            #         111.45,
            #         106.1,
            #         99.21,
            #         93.67,  # 3
            #         94.09,
            #         105.29,
            #         120.04,
            #         173.78,
            #         190.46,
            #         204.99,
            #         205.3,  # 3
            #         182.8,
            #         141.91,
            #     ],
            #     "export": [
            #         116.42,
            #         83.47,
            #         77.35,
            #         91.11,
            #         94.7,
            #         113.91,
            #         130.81,
            #         139.59,
            #         126.37,
            #         116.43,
            #         104.72,
            #         88.19,
            #         74.03,
            #         52.54,
            #         42.44,
            #         39.1,  # 1
            #         46.67,
            #         74.65,
            #         93.59,
            #         110.24,  # 1
            #         107.9,
            #         101.48,
            #         89.55,
            #         42.13,
            #         23.54,
            #         25.12,
            #         18.62,  # 2
            #         21.38,
            #         23.21,
            #         23.83,
            #         32.23,
            #         39.27,
            #         94.33,  # 2
            #         81.14,
            #         62.29,
            #         50.2,
            #         45.92,
            #         40.41,
            #         35.98,  # 3
            #         36.31,
            #         45.27,
            #         57.07,
            #         100.06,
            #         113.41,
            #         125.03,
            #         125.28,  # 3
            #         107.28,
            #         74.57,
            #     ],
            #     "yield": 1.0,
            #     "plan": [
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         -1000,  # 1
            #         0,
            #         0,
            #         0,
            #         1000,  # 1
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         -1000,  # 2
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         1000,  # 2
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         -1000,  # 3
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         0,
            #         1000,  # 3
            #         0,
            #         0,
            #     ],
            # },
        ],
    )
    def test_charge_cost(
        self,
        planner: Planner,
        battery_one_kw_one_kwh: Battery,
        prices: dict[str, list[float]],
    ):
        charge_plan = planner.create_price_arbitrage_plan(
            battery_one_kw_one_kwh,
            prices["import"],
            prices["export"],
        )
        assert charge_plan.expected_yield() == prices["yield"], f"\n{charge_plan}"
        if "plan" in prices:
            for hour, power in enumerate(prices["plan"]):
                assert charge_plan.get_by_index(hour).get_power_watts() == power

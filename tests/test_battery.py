from custom_components.battery_planner.battery import Battery
from custom_components.battery_planner.charge_hour import ChargeHour
from .fixtures import *


class TestBattery:
    def test_charge_should_update_average_charge_cost(
        self, battery_one_kw_one_kwh: Battery
    ):
        """Test that average charge cost is updated when charging the battery"""
        battery_one_kw_one_kwh.charge_max_power_for_one_hour(
            ChargeHour(hour=0, import_price=2, export_price=1, power=0)
        )
        assert battery_one_kw_one_kwh.get_average_charge_cost() == 2.0

    def test_charge_twice_should_update_average_charge_cost(
        self, battery_one_kw_two_kwh: Battery
    ):
        """Test that average charge cost is updated when charging the battery"""
        battery_one_kw_two_kwh.charge_max_power_for_one_hour(
            ChargeHour(hour=0, import_price=2, export_price=1, power=0)
        )
        assert battery_one_kw_two_kwh.get_average_charge_cost() == 2.0
        battery_one_kw_two_kwh.charge_max_power_for_one_hour(
            ChargeHour(hour=1, import_price=5, export_price=4, power=0)
        )
        assert battery_one_kw_two_kwh.get_average_charge_cost() == (2 + 5) / 2

    def test_charge_should_return_power(self, battery_one_kw_one_kwh: Battery):
        """Test power is set when charging the battery"""
        charge_hour = ChargeHour(hour=0, import_price=2, export_price=1, power=0)
        assert (
            battery_one_kw_one_kwh.charge_max_power_for_one_hour(charge_hour) == -1000
        )

    def test_discharge_should_return_power(self, battery_one_kw_one_kwh: Battery):
        """Test power is set when charging the battery"""
        battery_one_kw_one_kwh.charge_max_power_for_one_hour(
            ChargeHour(hour=1, import_price=5, export_price=4, power=0)
        )
        assert battery_one_kw_one_kwh.discharge_max_power_for_one_hour() == 1000

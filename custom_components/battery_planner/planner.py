"""Planner module"""

import logging

from .charge_plan import ChargePlan
from .battery import Battery
from .charge_hour import ChargeHour


_LOGGER = logging.getLogger(__name__)

API_PATH = "custom_components.battery_planner.api"
SECRETS_PATH = "secrets.json"


class Planner:
    """Logic algorithm class that creates a charge plan based on a list of electricity prices"""

    _low_price_threshold: float
    _planned_hours: list[ChargeHour]

    def __init__(
        self,
        low_price_threshold: float,
    ):
        self._low_price_threshold = low_price_threshold
        self._planned_hours = []

    def create_price_arbitrage_plan(
        self,
        battery: Battery,
        import_prices: list[float],
        export_prices: list[float],
        start_hour: int = 0,
    ) -> ChargePlan:
        """Charge plan is created for the period specified by the provided hours

        The battery may have a minimum state of charge setting, which will decrease the
        actual available capacity of the battery. However, we can set the battery_capacity
        to ~5% higher than the actual available capacity to ensure that it is fully charged
        and discharged. Therefore it is fine to use the full capacity of the battery if the
        minimum SoC is set to e.g. 5%.

        battery - Battery to be charged and discharged
        import_prices - Import prices (price/kWh) where the first item is for 00:00 today
        export_prices - Export prices (price/kWh) where the first item is for 00:00 today
        start_hour - The first hour (from midnight today) to create plan for

        Returns a plan with 0 W for all hours if the return is to low"""

        import_prices = import_prices[start_hour:]
        export_prices = export_prices[start_hour:]
        charge_plan = _empty_charge_plan(
            _map_prices_to_hour(import_prices, export_prices, start_hour)
        )
        initial_battery = battery.clone()
        self._planned_hours = []
        # TODO: Don't have the battery degradation cost included in the import_price series. Add it
        # later to the import price so that the yield calculation is based on only the grid prices.
        # Maybe add it to all the import prices here while creating the plan, then subtract it
        # again so that the resulting charge plan only calculates yield based on the grid price.

        self._charge_low_and_discharge_high(charge_plan.get_hours_list(), battery)
        self._find_and_fill_gaps(charge_plan.get_hours_list(), initial_battery)

        if charge_plan.is_empty_plan():
            self._charge_if_price_is_below_threshold(battery, charge_plan)

        return charge_plan

    def _charge_if_price_is_below_threshold(
        self, battery: Battery, charge_plan: ChargePlan
    ):
        print(battery)
        for hour in sorted(
            charge_plan.get_hours_list(), key=lambda h: h.get_import_price()
        ):
            if (
                hour.get_import_price() < self._low_price_threshold
                and not battery.is_full()
            ):
                hour.set_power(battery.charge_max_power_for_one_hour(hour))

    def _charge_low_and_discharge_high(
        self,
        charge_hours: list[ChargeHour],
        battery: Battery,
        reverse: bool = False,
    ) -> None:
        lowest_import_price: list[ChargeHour] = sorted(
            charge_hours, key=lambda hour: hour.get_import_price()
        )
        highest_export_first: list[ChargeHour] = sorted(
            charge_hours,
            key=lambda hour: hour.get_export_price(),
            reverse=True,
        )
        initial_average_charge_cost = battery.get_average_charge_cost()
        last_charged_hour_index = self._charge_battery_full_at_lowest_price(
            lowest_import_price, highest_export_first, battery, reverse
        )
        self._discharge_at_highest_priced_hours(
            highest_export_first,
            last_charged_hour_index,
            battery,
            initial_average_charge_cost,
            reverse,
        )

    def _charge_battery_full_at_lowest_price(
        self,
        lowest_import_first: list[ChargeHour],
        highest_export_first: list[ChargeHour],
        battery: Battery,
        reverse: bool = False,
    ) -> int:
        last_charged_hour_index = -1
        for discharge_hour in highest_export_first:
            for charge_hour in lowest_import_first:
                charge_comes_before_discharge = (
                    charge_hour.get_index() < discharge_hour.get_index()
                )
                if reverse:
                    charge_comes_before_discharge = (
                        charge_hour.get_index() > discharge_hour.get_index()
                    )
                if (
                    charge_comes_before_discharge
                    and charge_hour.get_import_price()
                    < discharge_hour.get_export_price()
                    and discharge_hour.get_export_price()
                    > battery.get_average_charge_cost()
                    and not battery.is_full()
                    and charge_hour.get_power() == 0
                ):
                    charge_hour.set_power(
                        battery.charge_max_power_for_one_hour(charge_hour)
                    )
                    last_charged_hour_index = charge_hour.get_index()
        return last_charged_hour_index

    def _discharge_at_highest_priced_hours(
        self,
        highest_export_first: list[ChargeHour],
        last_charged_hour_index: int,
        battery: Battery,
        inital_average_charge_cost: float,
        reverse: bool = False,
    ):
        average_charge_cost = battery.get_average_charge_cost()
        if reverse:
            average_charge_cost = inital_average_charge_cost

        for discharge_hour in highest_export_first:
            discharge_comes_after_last_charge = (
                discharge_hour.get_index() > last_charged_hour_index
            )
            if reverse:
                discharge_comes_after_last_charge = (
                    discharge_hour.get_index() < last_charged_hour_index
                )
            if (
                (battery.remaining_energy_above_lower_soc_limit() > 0)
                and (discharge_hour.get_export_price() > average_charge_cost)
                and discharge_comes_after_last_charge
            ):
                discharge_hour.set_power(battery.discharge_max_power_for_one_hour())

    def _find_and_fill_gaps(
        self, charge_hours: list[ChargeHour], battery: Battery
    ) -> None:
        charge_hours = sorted(charge_hours, key=lambda h: h.get_time())

        charging_hours: list[ChargeHour] = list(
            filter(lambda h: h.get_power() < 0, charge_hours)
        )
        discharging_hours: list[ChargeHour] = list(
            filter(lambda h: h.get_power() > 0, charge_hours)
        )

        first_charge_index = -1
        last_charge_index = -1
        if charging_hours:
            first_charge_index = charge_hours.index(charging_hours[0])
            last_charge_index = charge_hours.index(charging_hours[-1])

        first_discharge_index = len(charge_hours)
        last_discharge_index = len(charge_hours)
        if discharging_hours:
            first_discharge_index = charge_hours.index(discharging_hours[0])
            last_discharge_index = charge_hours.index(discharging_hours[-1])

        # Gap before first charge
        if 0 < first_charge_index < first_discharge_index:
            hours = charge_hours[0:first_charge_index]
            self._charge_low_and_discharge_high(hours, battery)

        # Gap before first discharge when battery was charged from start
        elif first_discharge_index < len(charge_hours):
            hours = charge_hours[0:first_discharge_index]
            empty_battery = battery.empty_clone(True)
            empty_battery.set_average_charge_cost(battery.get_average_charge_cost())
            self._charge_low_and_discharge_high(hours, empty_battery, reverse=True)

        # Gap between charge and discharge
        if -1 < last_charge_index < first_discharge_index < len(charge_hours):
            hours = charge_hours[last_charge_index + 1 : first_discharge_index]
            self._charge_low_and_discharge_high(
                hours, battery.empty_clone(True), reverse=True
            )

        # Gap after last discharge
        if last_charge_index < last_discharge_index < len(charge_hours):
            hours = charge_hours[last_discharge_index + 1 :]
            self._charge_low_and_discharge_high(hours, battery.empty_clone(True))


def _map_prices_to_hour(
    import_prices: list[float], export_prices: list[float], start_hour: int
) -> list[ChargeHour]:
    """Pair prices with correct hour"""
    prices: list[ChargeHour] = []
    for index, import_price in enumerate(import_prices):
        price = ChargeHour(
            hour=index + start_hour,
            import_price=import_price,
            export_price=export_prices[index],
            power=0,
        )
        prices.append(price)
    return prices


def _empty_charge_plan(charge_hours: list[ChargeHour]) -> ChargePlan:
    charge_plan = ChargePlan()
    for charge_hour in charge_hours:
        charge_plan.add_charge_hour(charge_hour)
    return charge_plan

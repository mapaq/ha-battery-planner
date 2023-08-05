"""Planner module"""

import logging
from datetime import datetime, time, timedelta

from .charge_plan import ChargePlan
from .battery import Battery
from .charge_hour import ChargeHour


_LOGGER = logging.getLogger(__name__)

API_PATH = "custom_components.battery_planner.api"
SECRETS_PATH = "secrets.json"


class Planner:
    """Logic algorithm class that creates a charge plan based on a list of electricity prices"""

    _cheap_import_price_limit: float

    def __init__(
        self,
        cheap_import_price_limit: float,
    ):
        self._cheap_import_price_limit = cheap_import_price_limit

    def create_price_arbitrage_plan(
        self, battery: Battery, import_prices: list[float], export_prices: list[float]
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

        Returns a plan with 0 W for all hours if the return is to low"""

        now = datetime.now()
        today_midnight = datetime.combine(now.date(), time(hour=0))
        empty_charge_plan = _empty_charge_plan(
            _map_prices_to_hour(import_prices, export_prices)
        )
        best_plans = {"best": empty_charge_plan.clone()}
        count = [0]  # TODO: Remove when finished
        self._create_charge_plans(
            best_plans, empty_charge_plan, today_midnight, battery, count
        )

        # print(f"Number of plans created: {count[0]}") # TODO: Remove when finished
        return best_plans["best"]

    def _create_charge_plans(
        self,
        best_plans: dict[str, ChargePlan],
        charge_plan: ChargePlan,
        hour_dt: datetime,
        battery: Battery,
        count: list[int],
    ):
        if not charge_plan.is_scheduled(hour_dt):
            count[0] += 1
            if charge_plan.expected_yield() > best_plans["best"].expected_yield():
                best_plans["best"] = charge_plan.clone()
            return

        charge_hour = charge_plan.get(hour_dt)
        next_hour_dt = hour_dt + timedelta(hours=1)

        charge_next_hour_plan = None
        idle_next_hour_plan = None
        discharge_next_hour_plan = None

        charge_next_hour_plan = charge_plan.clone()
        idle_next_hour_plan = charge_plan.clone()
        discharge_next_hour_plan = charge_plan.clone()

        charged_battery = battery.clone()
        if _is_possible_charge_hour(charge_plan, charge_hour, charged_battery):
            hour_to_charge = charge_hour.clone()
            charged_battery.charge_max_power_for_one_hour(hour_to_charge)
            charge_next_hour_plan.add_charge_hour(hour_to_charge)
            self._create_charge_plans(
                best_plans,
                charge_next_hour_plan.clone(),
                next_hour_dt,
                charged_battery.clone(),
                count,
            )

        self._create_charge_plans(
            best_plans,
            idle_next_hour_plan.clone(),
            next_hour_dt,
            battery.clone(),
            count,
        )

        # TODO: Handle special case when battery is already charged.
        # The first hour can then be a discharge hour.
        # It may be enough to compare to average_charge_price instead of previous hours
        discharged_battery = battery.clone()
        if _is_possible_discharge_hour(charge_plan, charge_hour, discharged_battery):
            hour_to_discharge = charge_hour.clone()
            discharged_battery.discharge_max_power_for_one_hour(hour_to_discharge)
            discharge_next_hour_plan.add_charge_hour(hour_to_discharge)
            self._create_charge_plans(
                best_plans,
                discharge_next_hour_plan.clone(),
                next_hour_dt,
                discharged_battery.clone(),
                count,
            )


def _map_prices_to_hour(
    import_prices: list[float], export_prices: list[float]
) -> list[ChargeHour]:
    """Pair prices with correct hour.
    The first item in the list will be paired with the hour for midnight of today"""
    prices: list[ChargeHour] = []
    for index, import_price in enumerate(import_prices):
        price = ChargeHour(
            hour=index,
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


def _is_possible_charge_hour(
    charge_plan: ChargePlan, charge_hour: ChargeHour, battery: Battery
):
    return not battery.is_full() and _is_lowest_price_before_next_discharge(
        charge_hour, charge_plan
    )


def _is_lowest_price_before_next_discharge(
    charge_hour: ChargeHour, charge_plan: ChargePlan
) -> bool:
    index = charge_hour.get_hour()
    cheapest_charge_hour = charge_hour
    next_possible_discharge_hour = None

    for index in range(index + 1, len(charge_plan.get_scheduled_hours())):
        next_hour = charge_plan.get_by_index(index)
        if next_hour.get_export_price() > cheapest_charge_hour.get_import_price():
            next_possible_discharge_hour = next_hour
            break
        if next_hour.get_import_price() < cheapest_charge_hour.get_import_price():
            cheapest_charge_hour = next_hour

    if next_possible_discharge_hour is None:
        return False

    return charge_hour.get_hour() == cheapest_charge_hour.get_hour()


def _is_possible_discharge_hour(
    charge_plan: ChargePlan, charge_hour: ChargeHour, battery: Battery
):
    return (
        not battery.is_empty()
        and _export_price_is_larger_than_a_previous_import_price(
            charge_hour, charge_plan
        )
        and _is_highest_price_before_next_charge(charge_hour, charge_plan)
    )


def _is_highest_price_before_next_charge(
    charge_hour: ChargeHour, charge_plan: ChargePlan
) -> bool:
    index = charge_hour.get_hour()
    best_discharge_hour = charge_hour

    for index in range(index + 1, len(charge_plan.get_scheduled_hours())):
        next_hour = charge_plan.get_by_index(index)
        if _is_lowest_price_before_next_discharge(next_hour, charge_plan):
            break
        if next_hour.get_export_price() > best_discharge_hour.get_export_price():
            best_discharge_hour = next_hour

    return charge_hour.get_hour() == best_discharge_hour.get_hour()


# TODO: Replace with "_export_price_is_larger_than_average_charge_cost" for the battery
def _export_price_is_larger_than_a_previous_import_price(
    discharge_hour: ChargeHour, charge_plan: ChargePlan
) -> bool:
    possible_discharge_hour_index = discharge_hour.get_hour()
    # TODO: Replace the starting 0 index with the last discharge hour.
    # Hmm, might not need to do that? I only want to know if i can find
    # any charge hour before this hour, then stop the loop.
    for index in range(possible_discharge_hour_index - 1, -1, -1):
        previous_hour = charge_plan.get_by_index(index)
        if previous_hour.get_import_price() < discharge_hour.get_export_price():
            return True
    return False

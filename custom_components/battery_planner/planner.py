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

        # charge_hours = _map_prices_to_hour(import_prices, export_prices)
        # charge_plan = ChargePlan()

        # for i in range(len(charge_hours) - 1):
        #     if charge_hours[i].get_import_price() < charge_hours[i + 1].get_import_price():
        #         self._charge_battery(charge_plan, battery, charge_hours[i])

        now = datetime.now()
        today_midnight = datetime.combine(now.date(), time(hour=0))
        empty_charge_plan = _empty_charge_plan(
            _map_prices_to_hour(import_prices, export_prices)
        )
        charge_plans: list[ChargePlan] = []
        best_charge_plan = self._create_charge_plans(
            charge_plans, empty_charge_plan, today_midnight, battery, "-"
        )

        best_charge_plan = _find_best_charge_plan(charge_plans)

        return best_charge_plan

    def _create_charge_plans(
        self,
        charge_plans: list[ChargePlan],
        charge_plan: ChargePlan,
        hour_dt: datetime,
        battery: Battery,
        tree: str,
    ) -> ChargePlan:
        # print("\nbefore, tree = " + tree)
        # print(charge_plan)
        # print(f"{battery.get_energy()} : {battery.is_full()}")
        if not charge_plan.is_scheduled(hour_dt):
            # print("returning")
            # TODO: Could just set the currently best plan right here, update if better then current
            charge_plans.append(charge_plan.clone())
            return charge_plan

        charge_hour = charge_plan.get(hour_dt)
        next_hour_dt = hour_dt + timedelta(hours=1)

        charge_next_hour_plan = None
        idle_next_hour_plan = None
        discharge_next_hour_plan = None

        charged_battery = battery.clone()

        charge_next_hour_plan = charge_plan.clone()
        idle_next_hour_plan = charge_plan.clone()
        discharge_next_hour_plan = charge_plan.clone()
        # if battery.is_full():
        #     print(charge_plan)
        #     print(f"{battery.get_energy()} : {battery.is_full()}")
        #     print(f"{charged_battery.get_energy()} : {charged_battery.is_full()}")
        if not charged_battery.is_full():
            # print("\nnot full, charging, tree = " + tree)
            # print(charge_plan)
            # print(f"{battery.get_energy()} : {battery.is_full()}")
            # print(f"{charged_battery.get_energy()} : {charged_battery.is_full()}")
            ch = charge_hour.clone()
            charged_battery.charge_max_power_for_one_hour(ch)
            charge_next_hour_plan.add_charge_hour(ch)
            # print(charge_next_hour_plan)
            # print(f"{charged_battery.get_energy()} : {charged_battery.is_full()}")
            charge_next_hour_plan = self._create_charge_plans(
                charge_plans,
                charge_next_hour_plan.clone(),
                next_hour_dt,
                charged_battery.clone(),
                tree + "c",
            )

        # print("\nidle, tree = " + tree)
        # print(charge_plan)
        # print(f"{battery.get_energy()} : {battery.is_full()}")
        idle_next_hour_plan = self._create_charge_plans(
            charge_plans,
            idle_next_hour_plan.clone(),
            next_hour_dt,
            battery.clone(),
            tree + "i",
        )

        discharged_battery = battery.clone()
        if not discharged_battery.is_empty():
            # print("\nnot empty, discharging, tree = " + tree)
            # print(f"{battery.get_energy()} : {battery.is_full()}")
            # print(discharge_next_hour_plan)
            # print(f"{discharged_battery.get_energy()} : {charged_battery.is_full()}")
            ch = charge_hour.clone()
            discharged_battery.discharge_max_power_for_one_hour(ch)
            discharge_next_hour_plan.add_charge_hour(ch)
            discharge_next_hour_plan = self._create_charge_plans(
                charge_plans,
                discharge_next_hour_plan.clone(),
                next_hour_dt,
                discharged_battery.clone(),
                tree + "d",
            )

        # best_charge_plan = idle_next_hour_plan
        # if discharge_next_hour_plan is not None and (discharge_next_hour_plan.expected_yield() > idle_next_hour_plan.expected_yield()):
        #     best_charge_plan = discharge_next_hour_plan
        # elif charge_next_hour_plan is not None and (charge_next_hour_plan.expected_yield() > idle_next_hour_plan.expected_yield()):
        #     best_charge_plan = charge_next_hour_plan
        # elif charge_next_hour_plan is not None and discharge_next_hour_plan is not None and (charge_next_hour_plan.expected_yield() > discharge_next_hour_plan.expected_yield()):
        #     best_charge_plan = charge_next_hour_plan
        best_charge_plan = discharge_next_hour_plan
        if (
            idle_next_hour_plan.expected_yield()
            > discharge_next_hour_plan.expected_yield()
        ):
            best_charge_plan = idle_next_hour_plan
        elif (
            charge_next_hour_plan.expected_yield()
            > idle_next_hour_plan.expected_yield()
        ):
            best_charge_plan = charge_next_hour_plan

        return best_charge_plan


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


def _find_best_charge_plan(charge_plans: list[ChargePlan]) -> ChargePlan:
    best_charge_plan = charge_plans[0]
    for charge_plan in charge_plans:
        if charge_plan.expected_yield() > best_charge_plan.expected_yield():
            best_charge_plan = charge_plan
    return best_charge_plan

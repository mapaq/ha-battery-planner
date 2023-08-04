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
        self._create_charge_plans(
            best_plans, empty_charge_plan, today_midnight, battery
        )

        return best_plans["best"]

    def _create_charge_plans(
        self,
        best_plans: dict[str, ChargePlan],
        charge_plan: ChargePlan,
        hour_dt: datetime,
        battery: Battery,
    ):
        if not charge_plan.is_scheduled(hour_dt):
            if charge_plan.expected_yield() > best_plans["best"].expected_yield():
                best_plans["best"] = charge_plan.clone()
            return

        charge_hour = charge_plan.get(hour_dt)
        next_hour_dt = hour_dt + timedelta(hours=1)

        charge_next_hour_plan = None
        idle_next_hour_plan = None
        discharge_next_hour_plan = None

        charged_battery = battery.clone()

        charge_next_hour_plan = charge_plan.clone()
        idle_next_hour_plan = charge_plan.clone()
        discharge_next_hour_plan = charge_plan.clone()

        if not charged_battery.is_full():
            hour_to_charge = charge_hour.clone()
            charged_battery.charge_max_power_for_one_hour(hour_to_charge)
            charge_next_hour_plan.add_charge_hour(hour_to_charge)
            self._create_charge_plans(
                best_plans,
                charge_next_hour_plan.clone(),
                next_hour_dt,
                charged_battery.clone(),
            )

        self._create_charge_plans(
            best_plans,
            idle_next_hour_plan.clone(),
            next_hour_dt,
            battery.clone(),
        )

        discharged_battery = battery.clone()
        if not discharged_battery.is_empty():
            hour_to_discharge = charge_hour.clone()
            discharged_battery.discharge_max_power_for_one_hour(hour_to_discharge)
            discharge_next_hour_plan.add_charge_hour(hour_to_discharge)
            self._create_charge_plans(
                best_plans,
                discharge_next_hour_plan.clone(),
                next_hour_dt,
                discharged_battery.clone(),
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


def _find_best_charge_plan(charge_plans: list[ChargePlan]) -> ChargePlan:
    best_charge_plan = charge_plans[0]
    for charge_plan in charge_plans:
        if charge_plan.expected_yield() > best_charge_plan.expected_yield():
            best_charge_plan = charge_plan
    return best_charge_plan

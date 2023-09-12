"""Planner module"""

import logging
import math
from datetime import datetime, time, timedelta
from typing import Callable

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

        # now = datetime.now()
        # today_midnight = datetime.combine(now.date(), time(hour=0))
        empty_charge_plan = _empty_charge_plan(
            _map_prices_to_hour(import_prices, export_prices)
        )
        # best_plans = {"best": empty_charge_plan.clone()}
        # self._create_charge_plans(
        #     best_plans, empty_charge_plan, today_midnight, battery
        # )
        new_plan = self._new_plan(empty_charge_plan, battery)
        # print(f"\n{new_plan}")

        return new_plan
        # return best_plans["best"]

    def _new_plan_two(self, charge_plan: ChargePlan, battery: Battery) -> ChargePlan:
        time_sorted_hours = charge_plan.get_hours_list()
        low_import_price_first = sorted(
            time_sorted_hours,
            key=lambda hour: hour.get_import_price(),
        )

        # charging_hours: list[ChargeHour] = []
        # discharging_hours: list[ChargeHour] = []

        # index = 0
        # while index < len(low_import_first):
        #     if _can_discharge_after(low_import_first[index], low_import_first):
        #         charging_hour = low_import_first.pop(index)
        #         charging_hour.set_power_watts(-1)
        #         charging_hours.append(charging_hour)
        #         discharging_hour = _find_possible_discharge_hours_after(
        #             charging_hour, low_import_first
        #         )  # When removing best discharge after, a charge hour after this charge hour may need this discharge hour
        #         discharging_hour.set_power_watts(1)
        #         discharging_hours.append(discharging_hour)
        #     else:
        #         index += 1

        # for hour in low_import_price_first:
        #     if _can_discharge_after(hour, low_import_price_first):
        #         if _is_possible_discharge_hour(hour):
        #             hour.set_power_watts(11)
        #         else:
        #             hour.set_power_watts(-1)
        #         _mark_possible_discharge_hours_after(hour, low_import_price_first)
        #     if (
        #         not battery.is_empty()
        #         and battery.get_average_charge_cost() < hour.get_export_price()
        #     ):
        #         hour.set_power_watts(11)

        # for hour in low_import_price_first:
        #     if _can_discharge_after(hour, low_import_price_first):
        #         hour.set_power_watts(-1)
        #         _mark_possible_discharge_hours_after(hour, low_import_price_first)
        #     if (
        #         not battery.is_empty()
        #         and battery.get_average_charge_cost() < hour.get_export_price()
        #     ):
        #         hour.set_power_watts(11)

        # print(f"\n{charge_plan}")

        # print()
        # for h in low_import_price_first:
        #     print(h)

        # for hour in time_sorted_hours:
        #     if hour.get_power_watts() == -1:
        #         possible_discharge_hours = (
        #             _get_possible_discharge_hours_between_this_and_next_charge(
        #                 hour, time_sorted_hours
        #             )
        #         )
        #         high_export_price_last = sorted(
        #             possible_discharge_hours, key=lambda hour: hour.get_export_price()
        #         )
        #         if high_export_price_last:
        #             best_discahrge_hour = high_export_price_last.pop()
        #             best_discahrge_hour.set_power_watts(2)

        # time_sorted_hours_reverse = sorted(
        #     time_sorted_hours, key=lambda hour: hour.get_time(), reverse=True
        # )
        # for hour in time_sorted_hours_reverse:
        #     if hour.get_power_watts() == 2:
        #         possible_charge_hours = (
        #             _get_possible_charge_hours_between_this_and_previous_discharge(
        #                 hour, time_sorted_hours_reverse
        #             )
        #         )
        #         low_import_price_last = sorted(
        #             possible_charge_hours,
        #             key=lambda hour: hour.get_import_price(),
        #             reverse=True,
        #         )
        #         if low_import_price_last:
        #             best_charge_hour = low_import_price_last.pop()
        #             best_charge_hour.set_power_watts(-2)

        # TODO: Do the same thing backwards. For each discharge hour, find the best charge hour
        # between the current discharge hour and the previous one

        # for hour in low_import_first:
        #     charge_plan.add_charge_hour(hour)

        # for hour in charging_hours + discharging_hours:
        #     charge_plan.add_charge_hour(hour)

        # print(charging_hours)
        # print()
        # print(discharging_hours)

        # filtered_charge_plan = ChargePlan()
        # sorted_by_time = sorted(
        #     charging_hours + discharging_hours, key=lambda hour: hour.get_time()
        # )
        # for index, hour in enumerate(sorted_by_time):
        #     hour._hour = (
        #         index  # TODO: Fix, don't use private parameter and don't change index
        #     )
        #     filtered_charge_plan.add_charge_hour(hour)
        # print(filtered_charge_plan)
        print(f"\n{charge_plan}")
        best_plan = self._create_best_charge_plan(charge_plan, battery)

        # for hour_iso in charge_plan.get_hours_dict():
        #     if hour_iso in best_plan.get_hours_dict():
        #         charge_plan.add_charge_hour(best_plan.get(hour_iso))

        return best_plan

    def _new_plan(self, charge_plan: ChargePlan, battery: Battery) -> ChargePlan:
        self._find_and_mark_charge_and_discharge_hours(charge_plan)
        self._mark_possible_discharge_hours_with_power(charge_plan, battery, 2)
        self._mark_possible_charge_hours_with_power(charge_plan, battery, -2)
        print(f"\n{charge_plan}\n")
        for hour in charge_plan.get_hours_list():
            if abs(hour.get_power()) == 1:
                hour.set_power(0)

        # TODO: Reduce number of 1 and -2 by finding out how many hours are needed to fully charge
        # respectively discharge the battery. If only two are needed, a series of five 1 can be reduced to two.

        self._find_and_mark_charge_and_discharge_hours(charge_plan)
        self._mark_possible_discharge_hours_with_power(charge_plan, battery, 2)
        self._mark_possible_charge_hours_with_power(charge_plan, battery, -2)
        print(f"\n{charge_plan}\n")
        for hour in charge_plan.get_hours_list():
            if abs(hour.get_power()) == 1:
                hour.set_power(0)
            if abs(hour.get_power()) == 2:
                hour.set_power(int(hour.get_power() * 0.5))

        self._find_and_mark_charge_and_discharge_hours(charge_plan)
        self._mark_possible_discharge_hours_with_power(charge_plan, battery, 2)
        self._mark_possible_charge_hours_with_power(charge_plan, battery, -2)
        print(f"\n{charge_plan}\n")
        for hour in charge_plan.get_hours_list():
            if abs(hour.get_power()) == 1:
                hour.set_power(0)

        # # TODO: While not plan changes, run again

        for hour in charge_plan.get_hours_list():
            if abs(hour.get_power()) == 1:
                hour.set_power(0)
            if abs(hour.get_power()) == 2:
                hour.set_power(int(hour.get_power() * 0.5))

        print(f"\n{charge_plan}\n")

        # Remove unnecessary charge hours between discharge hours
        previous_discharge_hour_index = 0
        time_sorted_hours = sorted(
            charge_plan.get_hours_list(), key=lambda hour: hour.get_time()
        )
        for hour in time_sorted_hours:
            if hour.get_power() == 1:
                next_discharge_hour_index = time_sorted_hours.index(hour)
                charge_hours: list[ChargeHour] = []
                for charge_hour in time_sorted_hours[
                    previous_discharge_hour_index:next_discharge_hour_index
                ]:
                    if charge_hour.get_power() == -1:
                        charge_hours.append(charge_hour)
                        previous_discharge_hour_index = next_discharge_hour_index
                price_sorted = sorted(charge_hours, key=lambda h: h.get_import_price())
                for h in price_sorted[battery.needed_hours_to_fill() :]:
                    h.set_power(0)

        # agjfgjasdölfjjasdklfj
        self._find_and_mark_charge_and_discharge_hours(charge_plan)
        self._mark_possible_discharge_hours_with_power(charge_plan, battery, 2)
        self._mark_possible_charge_hours_with_power(charge_plan, battery, -2)
        print(f"\n{charge_plan}\n")
        for hour in charge_plan.get_hours_list():
            if abs(hour.get_power()) == 1:
                hour.set_power(0)
            if abs(hour.get_power()) == 2:
                hour.set_power(int(hour.get_power() * 0.5))

        #     discharge_hours: list[ChargeHour] = []
        # for hour in hours:
        #     if hour.get_time() > charge_hour.get_time():
        #         if _is_possible_charge_hour(hour) and discharge_hours:
        #             break  # A next possible charge hour was found
        #         if hour.get_power_watts() == 1 or hour.get_power_watts() == 2:
        #             discharge_hours.append(hour)

        # price_sorted_discharge_hours = sorted(
        #     discharge_hours, key=lambda hour: hour.get_export_price(), reverse=True
        # )
        # needed_hours_to_empty_battery = math.ceil(
        #     battery.get_available_capacity() / battery.get_max_discharge_power()
        # )
        # discharge_hours = price_sorted_discharge_hours[:needed_hours_to_empty_battery]

        # return discharge_hours

        # Remove unnecessary charge hours between discharge hours
        previous_discharge_hour_index = 0
        time_sorted_hours = sorted(
            charge_plan.get_hours_list(), key=lambda hour: hour.get_time()
        )
        for hour in time_sorted_hours:
            if hour.get_power() == 1:
                next_discharge_hour_index = time_sorted_hours.index(hour)
                charge_hours: list[ChargeHour] = []
                for charge_hour in time_sorted_hours[
                    previous_discharge_hour_index:next_discharge_hour_index
                ]:
                    if charge_hour.get_power() == -1:
                        charge_hours.append(charge_hour)
                        previous_discharge_hour_index = next_discharge_hour_index
                price_sorted = sorted(charge_hours, key=lambda h: h.get_import_price())
                for h in price_sorted[battery.needed_hours_to_fill() :]:
                    h.set_power(0)

        print(f"\n{charge_plan}\n")

        best_plan = self._create_best_charge_plan(charge_plan, battery)

        return best_plan

    def _mark_possible_discharge_hours_with_power(
        self, charge_plan: ChargePlan, battery: Battery, power: int
    ):
        is_charge_hour: Callable[[ChargeHour], bool]
        is_charge_hour = lambda hour: hour.get_power() < 0
        all_charge_hours = list(filter(is_charge_hour, charge_plan.get_hours_list()))
        for charge in all_charge_hours:
            discharge_group = (
                _get_possible_discharge_hours_between_this_and_next_charge(
                    charge, charge_plan.get_hours_list(), battery
                )
            )
            for hour in discharge_group:
                hour.set_power(power)

    def _mark_possible_charge_hours_with_power(
        self, charge_plan: ChargePlan, battery: Battery, power: int
    ):
        is_discharge_hour: Callable[[ChargeHour], bool]
        is_discharge_hour = lambda hour: hour.get_power() > 0
        all_discharge_hours = list(
            filter(is_discharge_hour, charge_plan.get_hours_list())
        )

        for discharge in all_discharge_hours:
            charge_hours = (
                _get_possible_charge_hours_between_this_and_previous_discharge(
                    discharge, charge_plan.get_hours_list(), battery
                )
            )
            for hour in charge_hours:
                hour.set_power(power)

    def _find_and_mark_charge_and_discharge_hours(self, charge_plan: ChargePlan):
        hours = charge_plan.get_hours_list()
        low_import_first = sorted(
            hours,
            key=lambda hour: hour.get_import_price(),
        )

        charge_hours_with_possible_discharge_hours: list[dict[str, object]] = []
        discharge_hours: list[ChargeHour] = []

        for charge_hour in low_import_first:
            discharge_hours = _find_all_possible_discharge_hours(
                charge_hour, charge_plan
            )
            if discharge_hours:
                entry = {}
                entry["charge_hour"] = charge_hour
                entry["discharge_hours"] = discharge_hours
                charge_hours_with_possible_discharge_hours.append(entry)

        charge_hours_with_possible_discharge_hours_sorted_last_hour_first = sorted(
            charge_hours_with_possible_discharge_hours,
            key=lambda entry: entry["charge_hour"].get_time(),  # type: ignore
            reverse=True,
        )

        for d in charge_hours_with_possible_discharge_hours_sorted_last_hour_first:
            charge: ChargeHour = d["charge_hour"]  # type: ignore
            if charge.get_power() == 0:
                charge.set_power(-1)

            discharges: list[ChargeHour] = d["discharge_hours"]  # type: ignore
            discharges = sorted(discharges, key=lambda hour: hour.get_export_price())
            while discharges:
                best_discharge = discharges.pop()
                if best_discharge.get_power() == 0:
                    best_discharge.set_power(1)
                    break

    def _create_best_charge_plan(self, charge_plan: ChargePlan, battery: Battery):
        now = datetime.now()
        today_midnight = datetime.combine(now.date(), time(hour=0))
        best_plan = {"best": charge_plan.clone()}
        self._create_charge_plans(best_plan, charge_plan, today_midnight, battery)
        return best_plan["best"]

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

        hour = charge_plan.get_by_dt(hour_dt)
        next_hour_dt = hour_dt + timedelta(hours=1)

        # is_possible_charge_hour = (
        #     hour.get_power_watts() == -2 or hour.get_power_watts() == 11
        # )
        # is_possible_discharge_hour = (
        #     hour.get_power_watts() == 2 or hour.get_power_watts() == 11
        # )

        is_possible_charge_hour = not battery.is_full() and hour.get_power() == -1

        is_possible_discharge_hour = (
            not battery.is_empty()
            and hour.get_export_price() > battery.get_average_charge_cost()
        ) or hour.get_power() == 1

        hour.set_power(0)

        charge_next_hour_plan = None
        idle_next_hour_plan = None
        discharge_next_hour_plan = None

        charge_next_hour_plan = charge_plan.clone()
        idle_next_hour_plan = charge_plan.clone()
        discharge_next_hour_plan = charge_plan.clone()

        charged_battery = battery.clone()
        if is_possible_charge_hour:
            hour_to_charge = hour.clone()
            charged_battery.charge_max_power_for_one_hour(hour_to_charge)
            charge_next_hour_plan.add_charge_hour(hour_to_charge)
            self._create_charge_plans(
                best_plans,
                charge_next_hour_plan.clone(),
                next_hour_dt,
                charged_battery.clone(),
            )

        discharged_battery = battery.clone()
        if is_possible_discharge_hour:
            hour_to_discharge = hour.clone()
            discharged_battery.discharge_max_power_for_one_hour()
            discharge_next_hour_plan.add_charge_hour(hour_to_discharge)
            self._create_charge_plans(
                best_plans,
                discharge_next_hour_plan.clone(),
                next_hour_dt,
                discharged_battery.clone(),
            )

        self._create_charge_plans(
            best_plans,
            idle_next_hour_plan.clone(),
            next_hour_dt,
            battery.clone(),
        )


def _map_prices_to_hour(
    import_prices: list[float], export_prices: list[float]
) -> list[ChargeHour]:
    """Pair prices with correct hour.
    The first item in the list will be paired with the hour for midnight of today"""
    # TODO: Remove past hours, only plan the future hours
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


def _get_possible_discharge_hours_between_this_and_next_charge(
    charge_hour: ChargeHour, hours: list[ChargeHour], battery: Battery
) -> list[ChargeHour]:
    discharge_hours: list[ChargeHour] = []
    time_sorted_hours = sorted(hours, key=lambda h: h.get_time())
    for hour in time_sorted_hours:
        if hour.get_time() > charge_hour.get_time():
            if _is_possible_charge_hour(hour) and discharge_hours:
                break  # A next possible charge hour was found
            if hour.get_power() == 1 or hour.get_power() == 2:
                # if hour.get_export_price() > charge_hour.get_import_price():
                discharge_hours.append(hour)

    price_sorted_discharge_hours = sorted(
        discharge_hours, key=lambda hour: hour.get_export_price(), reverse=True
    )
    discharge_hours = price_sorted_discharge_hours[: battery.needed_hours_to_deplete()]

    return discharge_hours


def _get_possible_charge_hours_between_this_and_previous_discharge(
    discharge_hour: ChargeHour, hours: list[ChargeHour], battery: Battery
) -> list[ChargeHour]:
    time_sorted_hours = sorted(hours, key=lambda hour: hour.get_time(), reverse=True)
    charge_hours: list[ChargeHour] = []
    for hour in time_sorted_hours:
        if hour.get_time() < discharge_hour.get_time():
            if _is_possible_discharge_hour(hour) and charge_hours:
                break  # A previous possible discharge hour was found
            if hour.get_power() == -1 or hour.get_power() == -2:
                charge_hours.append(hour)

    price_sorted_charge_hours = sorted(
        charge_hours, key=lambda hour: hour.get_import_price()
    )
    charge_hours = price_sorted_charge_hours[: battery.needed_hours_to_fill()]

    return charge_hours


def _get_best_charge_hour_between_this_and_previous_discharge(
    discharge_hour: ChargeHour, hours: list[ChargeHour]
) -> ChargeHour:
    charge_hours: list[ChargeHour] = []
    for hour in hours:
        if hour.get_time() < discharge_hour.get_time():
            if _is_possible_discharge_hour(hour) and charge_hours:
                break  # A previous possible discharge hour was found
            if hour.get_power() == -1:
                charge_hours.append(hour)
    return sorted(charge_hours, key=lambda hour: hour.get_import_price()).pop(0)


def _is_possible_charge_hour(hour: ChargeHour):
    power = hour.get_power()
    return power == -1 or power == -2


def _is_possible_discharge_hour(hour: ChargeHour):
    power = hour.get_power()
    return power == 1 or power == 2


def _can_discharge_after(charge_hour: ChargeHour, hours: list[ChargeHour]) -> bool:
    for discharge_hour in hours:
        if (
            charge_hour.get_import_price() < discharge_hour.get_export_price()
            and charge_hour.get_time() < discharge_hour.get_time()
        ):
            return True
    return False


def _mark_possible_discharge_hours_after(
    charge_hour: ChargeHour, hours: list[ChargeHour]
) -> None:
    # if charge_hour.get_export_price() == 25.99:
    #     print()
    for hour in hours:
        # if charge_hour.get_export_price() == 25.99:
        #     print(f"\n{charge_hour.get_import_price()} : {hour.get_export_price()}")
        #     print(f"{charge_hour.get_time()} : {hour.get_time()}")
        #     print(
        #         f"{charge_hour.get_import_price() < hour.get_export_price()} : {charge_hour.get_time() < hour.get_time()}"
        #     )
        if (
            charge_hour.get_import_price() < hour.get_export_price()
            and charge_hour.get_time() < hour.get_time()
        ):
            hour.set_power(1)
            # print(hour)


def _find_all_possible_discharge_hours(
    charge_hour: ChargeHour, charge_plan: ChargePlan
) -> list[ChargeHour]:
    discharge_hours = []
    for hour in charge_plan.get_hours_list():
        if (
            charge_hour.get_import_price() < hour.get_export_price()
            and charge_hour.get_time() < hour.get_time()
            and abs(hour.get_power()) != 2
        ):
            discharge_hours.append(hour)
    return discharge_hours


# def _is_possible_charge_hour(
#     charge_plan: ChargePlan, charge_hour: ChargeHour, battery: Battery
# ):
#     return (
#         not battery.is_full()
#         # and _is_lowest_price_before_next_discharge(charge_hour, charge_plan)
#         # and _is_local_min_import_price(charge_hour, charge_plan)
#     )


def _is_lowest_price_before_next_discharge(
    charge_hour: ChargeHour, charge_plan: ChargePlan
) -> bool:
    index = charge_hour.get_index()
    cheapest_charge_hour = charge_hour
    next_possible_discharge_hour = None

    for index in range(index + 1, charge_plan.len()):
        next_hour = charge_plan.get_by_index(index)
        if next_hour.get_export_price() > cheapest_charge_hour.get_import_price():
            next_possible_discharge_hour = next_hour
            break
        if next_hour.get_import_price() < cheapest_charge_hour.get_import_price():
            cheapest_charge_hour = next_hour

    if next_possible_discharge_hour is None:
        return False

    return charge_hour.get_index() == cheapest_charge_hour.get_index()


# def _is_possible_discharge_hour(
#     charge_plan: ChargePlan, charge_hour: ChargeHour, battery: Battery
# ):
#     return (
#         not battery.is_empty()
#         # and _export_price_is_larger_than_average_charge_cost(charge_hour, battery)
#         # and _is_highest_price_before_next_charge(charge_hour, charge_plan)
#         # and _is_local_max_export_price(charge_hour, charge_plan)
#     )


def _is_highest_price_before_next_charge(
    charge_hour: ChargeHour, charge_plan: ChargePlan
) -> bool:
    index = charge_hour.get_index()
    best_discharge_hour = charge_hour

    for index in range(index + 1, charge_plan.len()):
        next_hour = charge_plan.get_by_index(index)
        if _is_lowest_price_before_next_discharge(next_hour, charge_plan):
            break
        if next_hour.get_export_price() > best_discharge_hour.get_export_price():
            best_discharge_hour = next_hour

    return charge_hour.get_index() == best_discharge_hour.get_index()


def _export_price_is_larger_than_average_charge_cost(
    discharge_hour: ChargeHour, battery: Battery
) -> bool:
    return discharge_hour.get_export_price() > battery.get_average_charge_cost()


def _is_local_min_import_price(
    charge_hour: ChargeHour, charge_plan: ChargePlan
) -> bool:
    start_index = max(charge_hour.get_index() - 1, 0)
    end_index = min(charge_hour.get_index() + 1, charge_plan.len())
    previous_hour = charge_plan.get_by_index(start_index)
    next_hour = charge_plan.get_by_index(end_index)
    return (
        previous_hour.get_import_price()
        >= charge_hour.get_import_price()
        <= next_hour.get_import_price()
    )


def _is_local_max_export_price(
    charge_hour: ChargeHour, charge_plan: ChargePlan
) -> bool:
    start_index = max(charge_hour.get_index() - 1, 0)
    end_index = min(charge_hour.get_index() + 1, charge_plan.len() - 1)
    previous_hour = charge_plan.get_by_index(start_index)
    next_hour = charge_plan.get_by_index(end_index)
    return (
        previous_hour.get_export_price()
        <= charge_hour.get_export_price()
        >= next_hour.get_export_price()
    )

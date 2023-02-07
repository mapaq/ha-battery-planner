"""Example module to show how to implement the BatteryApiInterface"""

import logging
from datetime import datetime

from ...battery_api_interface import BatteryApiInterface
from ...charge_plan import ChargePlan

_LOGGER = logging.getLogger(__name__)


class ExampleBatteryApi(BatteryApiInterface):
    """Class to get and push schedules to the battery via Fronius SolarNet API"""

    _host: str
    _username: str
    _password: str
    _charge_plan: ChargePlan

    def __init__(self, secrets_json: dict[str:str]):
        super().__init__(secrets_json)
        self._host = secrets_json.get("host")
        self._username = secrets_json.get("username")
        self._password = secrets_json.get("password")
        self._charge_plan = None

    async def _login(self) -> bool:
        """Login is not part of the interface, but can be needed to perform before other requests"""
        _LOGGER.debug(
            "Login user %s@%s with password %s",
            self._username,
            self._host,
            self._password,
        )
        return True

    async def schedule_battery(self, new_charge_plan: ChargePlan) -> bool:
        """Create new schedule for the battery
        Return True if the scheduling succeeded"""
        await self._login()
        self._charge_plan = new_charge_plan
        return True

    async def get_active_charge_plan(self) -> ChargePlan:
        """Fetch the active charge plan from the battery API"""
        if self._charge_plan is not None:
            return self._charge_plan

        await self._login()
        charge_plan = ChargePlan()
        charge_plan.add(datetime.now().replace(hour=0), -1122, 1.15)
        charge_plan.add(datetime.now().replace(hour=1), 1234, 3.05)
        charge_plan.add(datetime.now().replace(hour=2), 3000, 2.0)
        charge_plan.add(datetime.now(), 4000, 1.7)
        return charge_plan

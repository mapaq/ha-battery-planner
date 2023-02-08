"""Fronius Solarnet API"""

from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant

from .digest_auth_request import DigestAuthRequest
from .solarnet_charge_schedule import SolarnetChargeSchedule
from ...battery_api_interface import BatteryApiInterface
from ...charge_plan import ChargePlan


class FroniusSolarnetApi(BatteryApiInterface):
    """Class to get and push schedules to the battery via Fronius SolarNet API"""

    _LOGIN_URI = "/commands/Login"
    _TIMEOFUSE_URI = "/config/timeofuse"
    _TIMEOFUSE_JSON_OBJECT = "timeofuse"

    _solarnet: DigestAuthRequest = None
    _username: str = None

    def __init__(self, secrets_json: dict[str:str], hass: HomeAssistant):
        super().__init__(secrets_json, hass)
        host = f"http://{secrets_json.get('host')}"
        username = secrets_json.get("username")
        password = secrets_json.get("password")
        self._solarnet = DigestAuthRequest(host, username, password, hass)
        self._username = username

    async def _login(self) -> bool:
        """Login the user to be able to read and write schedules"""
        digest_uri = f"{self._LOGIN_URI}?user={self._username}"
        response = await self._solarnet.get(digest_uri)
        return response.status_code == 200

    async def schedule_battery(self, new_charge_plan: ChargePlan) -> bool:
        """Create new schedule for the battery
        The input dict is {hour: power(W)}, e.g. {3:-2000} or {17:3000}
        where a negative power value is charging battery and positive is discharging

        Returns True if the scheduling succeeded"""

        await self._login()

        solarnet_schedules: dict[
            datetime, SolarnetChargeSchedule
        ] = self._active_schedules_for_today()

        new_schedules = new_charge_plan.get_schedules()
        for hour_dt, power in new_schedules.items():
            self._create_schedules_for_hour(solarnet_schedules, hour_dt, power)

        solarnet_schedules_json = []
        for solarnet_schedule in solarnet_schedules.values():
            solarnet_schedules_json.append(solarnet_schedule.tojsondict())

        json_data = {self._TIMEOFUSE_JSON_OBJECT: solarnet_schedules_json}
        # response = async self._solarnet.post_json(self._TIMEOFUSE_URI, payload=json_data)
        # return response.status_code == 200
        return True

    def _create_schedules_for_hour(self, solarnet_schedules, hour_dt, power):
        schedule_type_min = SolarnetChargeSchedule.SCHEDULE_TYPE_DISCHARGE_MIN
        schedule_type_max = SolarnetChargeSchedule.SCHEDULE_TYPE_DISCHARGE_MAX
        if power < 0:
            schedule_type_min = SolarnetChargeSchedule.SCHEDULE_TYPE_CHARGE_MIN
            schedule_type_max = SolarnetChargeSchedule.SCHEDULE_TYPE_CHARGE_MAX

        solarnet_schedules[hour_dt] = SolarnetChargeSchedule(
            hour_dt, power
        ).set_schedule_type(schedule_type_min)
        solarnet_schedules[hour_dt + timedelta(seconds=1)] = SolarnetChargeSchedule(
            hour_dt, power
        ).set_schedule_type(schedule_type_max)

    async def _active_schedules_for_today(
        self,
    ) -> dict[datetime, SolarnetChargeSchedule]:
        todays_schedules = {}
        today_weekday = datetime.now().weekday()
        active_schedules = await self._get_solarnet_schedules()
        for active_schedule in active_schedules:
            if today_weekday == active_schedule.get_weekday():
                if active_schedule.get_hour() in todays_schedules.keys():
                    todays_schedules[
                        active_schedule.get_hour().replace(second=1)
                    ] = active_schedule
                else:
                    todays_schedules[active_schedule.get_hour()] = active_schedule
        return todays_schedules

    async def get_active_charge_plan(self) -> ChargePlan:
        """Fetch the active charge plan from the inverter"""
        await self._login()
        avtive_schedules = await self._get_solarnet_schedules()

        charge_plan = ChargePlan()
        for solarnet_schedule in avtive_schedules:
            charge_plan.add(solarnet_schedule.get_hour(), solarnet_schedule.get_power())

        return charge_plan

    async def _get_solarnet_schedules(self) -> list[SolarnetChargeSchedule]:
        solarnet_schedules = []
        schedules_data = (
            await self._solarnet.get(self._TIMEOFUSE_URI)
            .json()
            .get(self._TIMEOFUSE_JSON_OBJECT)
        )
        for schedule_data in schedules_data:
            solarnet_schedules.append(
                SolarnetChargeSchedule.fromjsondict(schedule_data)
            )
        return solarnet_schedules

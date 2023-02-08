"""Solarnet Charge Schedule data object"""

import logging

from datetime import datetime, time, timedelta
import json

_LOGGER = logging.getLogger(__name__)


class SolarnetChargeSchedule:
    """Schedule object containing battery charge and discharge intervals
    Example json content:
    {
        "Active": true,
        "Power": 2600,
        "ScheduleType": "CHARGE_MIN",
        "TimeTable": {
            "Start": "05:00",
            "End": "08:00"
        },
        "Weekdays": {
            "Mon": true,
            "Tue": true,
            "Wed": true,
            "Thu": true,
            "Fri": true,
            "Sat": false,
            "Sun": false
        }
    }
    """

    SCHEDULE_TYPE_CHARGE_MIN = "CHARGE_MIN"
    SCHEDULE_TYPE_CHARGE_MAX = "CHARGE_MAX"
    SCHEDULE_TYPE_DISCHARGE_MIN = "DISCHARGE_MIN"
    SCHEDULE_TYPE_DISCHARGE_MAX = "DISCHARGE_MAX"

    KEY_ACTIVE = "Active"
    KEY_POWER = "Power"
    KEY_SCHEDULE_TYPE = "ScheduleType"
    KEY_TIME_TABLE = "TimeTable"
    KEY_TIME_TABLE_START = "Start"
    KEY_TIME_TABLE_END = "End"
    KEY_WEEKDAYS = "Weekdays"

    WEEK_DAYS = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

    _active: bool = None
    _power: int = None
    _schdule_type: str = None
    _time_table: dict[str, time] = None
    _weekday: int = None

    def __init__(self, hour_to_schedule: datetime = None, power: int = None):
        """The fronius solarnet API only takes the time of day as start and end, not the date.
        If using the input hour and power, a schedule with one hour interval is created"""
        self._active = True
        self._time_table = {}

        if hour_to_schedule is not None:
            start_time = hour_to_schedule.time()
            if start_time.hour == 23:
                # The SolarNet interface does not handle date in start and end time.
                # End time cannot be e.g. 00:00 since start must be earlier than end.
                # If end should be 00:00 (the next day) it must be set to 23:59 (the same day)
                end_time = start_time.replace(hour=start_time.hour, minute=59)
            else:
                end_time = start_time.replace(hour=(start_time.hour + 1), minute=0)
            self.set_start(start_time)
            self.set_end(end_time)
            self.set_weekday_index(hour_to_schedule.weekday())

        if power is not None:
            if power == 0:
                self.set_schedule_type(
                    SolarnetChargeSchedule.SCHEDULE_TYPE_DISCHARGE_MAX
                )
            elif power < 0:
                self.set_schedule_type(SolarnetChargeSchedule.SCHEDULE_TYPE_CHARGE_MIN)
            else:
                self.set_schedule_type(
                    SolarnetChargeSchedule.SCHEDULE_TYPE_DISCHARGE_MIN
                )
            self.set_power(abs(power))

    def __str__(self):
        return json.dumps(self.tojsondict())

    def __repr__(self):
        return json.dumps(self.tojsondict())

    def set_active(self, active: bool):
        """Set if schedule is active"""
        self._active = active
        return self

    def get_power(self) -> int:
        """Get the power level
        negative value means consumption (charging)
        positive meands production (dischargning)"""
        if self._schdule_type in (
            self.SCHEDULE_TYPE_CHARGE_MIN,
            self.SCHEDULE_TYPE_CHARGE_MAX,
        ):
            return -self._power
        return self._power

    def set_power(self, power: int):
        """Set power level"""
        self._power = power
        return self

    def set_schedule_type(self, schedule_type: str):
        """Set schedule type"""
        if not schedule_type in (
            self.SCHEDULE_TYPE_CHARGE_MIN,
            self.SCHEDULE_TYPE_CHARGE_MAX,
            self.SCHEDULE_TYPE_DISCHARGE_MIN,
            self.SCHEDULE_TYPE_DISCHARGE_MAX,
        ):
            raise ValueError(f"Unsupported schedule type {schedule_type}")

        self._schdule_type = schedule_type
        return self

    def get_hour(self) -> datetime:
        """Return the start hour as an integer"""
        now = datetime.now()
        today_weekday = now.weekday()
        day_delta = self._weekday - today_weekday
        if day_delta == -6:
            day_delta = 1
        if day_delta == 6:
            day_delta = -1
        schedule_date = (now + timedelta(days=day_delta)).date()
        schedule_time = time(self._time_table[self.KEY_TIME_TABLE_START].hour)
        return datetime.combine(schedule_date, schedule_time)

    def set_start(self, start: time):
        """Set start time"""
        self._time_table["Start"] = start
        return self

    def set_end(self, end: time):
        """Set end time"""
        self._time_table["End"] = end
        return self

    def get_weekday(self) -> int:
        """Get day index for the active weekday"""
        return self._weekday

    def set_weekday_index(self, weekday_index: int):
        """Set the active weekday index for this schedule"""
        self._weekday = weekday_index

    def set_weekday_name(self, weekday_name: str):
        """Set the active weekday index based on solarnet weekday name for this schedule"""
        weekday_index = list(self.WEEK_DAYS.keys())[
            list(self.WEEK_DAYS.values()).index(weekday_name)
        ]
        self.set_weekday_index(weekday_index)
        self._weekday = weekday_index

    def tojsondict(self) -> dict[str:object]:
        """Exports the data in the json format used by solarnet API"""
        schedule = {}
        schedule[self.KEY_ACTIVE] = self._active
        schedule[self.KEY_POWER] = self._power
        schedule[self.KEY_SCHEDULE_TYPE] = self._schdule_type
        time_table = {}
        time_table[SolarnetChargeSchedule.KEY_TIME_TABLE_START] = self._time_table[
            SolarnetChargeSchedule.KEY_TIME_TABLE_START
        ].strftime("%H:%M")
        time_table[SolarnetChargeSchedule.KEY_TIME_TABLE_END] = self._time_table[
            SolarnetChargeSchedule.KEY_TIME_TABLE_END
        ].strftime("%H:%M")
        schedule[self.KEY_TIME_TABLE] = time_table
        weekdays = {}
        for weekday_index, weekday_name in self.WEEK_DAYS.items():
            weekdays[weekday_name] = weekday_index == self._weekday
        schedule[self.KEY_WEEKDAYS] = weekdays
        return schedule

    @staticmethod
    def fromjsondict(json_dict: dict[str:object]):
        """Creates a Schedule from response data from SolarNet API"""
        schedule = SolarnetChargeSchedule()

        for key, value in json_dict.items():
            if key == SolarnetChargeSchedule.KEY_ACTIVE:
                schedule.set_active(value)
            elif key == SolarnetChargeSchedule.KEY_POWER:
                schedule.set_power(value)
            elif key == SolarnetChargeSchedule.KEY_SCHEDULE_TYPE:
                schedule.set_schedule_type(value)
            elif key == SolarnetChargeSchedule.KEY_TIME_TABLE:
                schedule.set_start(
                    datetime.strptime(
                        value[SolarnetChargeSchedule.KEY_TIME_TABLE_START], "%H:%M"
                    ).time()
                )
                schedule.set_end(
                    datetime.strptime(
                        value[SolarnetChargeSchedule.KEY_TIME_TABLE_END], "%H:%M"
                    ).time()
                )
            elif key == SolarnetChargeSchedule.KEY_WEEKDAYS:
                for weekday_name, weekday_active in value.items():
                    if weekday_active and (
                        weekday_name in SolarnetChargeSchedule.WEEK_DAYS.values()
                    ):
                        schedule.set_weekday_name(weekday_name)
        return schedule

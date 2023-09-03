"""Object holding price and charge data for one hour"""

import logging
from datetime import datetime, timedelta, time

_LOGGER = logging.getLogger(__name__)


class ChargeHour:
    """Data class to hold charge level and import and export prices for an hour"""

    _hour: int
    _hour_dt: datetime
    _import_price: float
    _export_price: float
    _power_watts: int

    def __init__(self, hour: int, import_price: float, export_price: float, power: int):
        self.set_hour(hour)
        self._import_price = round(import_price, 2)
        self._export_price = round(export_price, 2)
        self._power_watts = power

    @classmethod
    def from_dt(
        cls, hour_dt: datetime, import_price: float, export_price: float, power: int
    ):
        """Create a ChargeHour object where the hour is represented by a datetime object"""
        tomorrow = (datetime.now() + timedelta(days=1)).day
        hour_index = 0
        if hour_dt.day == tomorrow:
            hour_index = 24
        hour_index += hour_dt.hour

        return ChargeHour(hour_index, import_price, export_price, power)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        readable = {}
        readable["Index"] = self.get_index()
        readable["Hour"] = self.hour_iso_string()
        readable["Import price"] = self._import_price
        readable["Export price"] = self._export_price
        readable["Power"] = self._power_watts
        return str(readable)

    def to_json(self) -> dict[str, str | float | int]:
        """Get data for the charge hour in JSON format"""
        return {
            "index": self.get_index(),
            "hour": self.hour_iso_string(),
            "import_price": self._import_price,
            "export_price": self._export_price,
            "power": self._power_watts,
        }

    def clone(self):
        """Create a clone of this object"""
        return ChargeHour(
            hour=self.get_index(),
            import_price=self.get_import_price(),
            export_price=self.get_export_price(),
            power=self.get_power_watts(),
        )

    def set_hour(self, hour: int):
        """Set hour from an int where 0 equals midnight today, save as a datetime object"""
        self._hour = hour
        now = datetime.now()
        today_midnight = datetime.combine(now.date(), time(0))
        self._hour_dt = today_midnight + timedelta(hours=hour)

    def get_index(self) -> int:
        """Get the hour as index (0 = today midnight)"""
        return self._hour

    def get_time(self) -> datetime:
        """Get the hour as datetime"""
        return self._hour_dt

    def hour_iso_string(self) -> str:
        """Get string representation of the hour as ISO format"""
        return datetime.combine(
            self._hour_dt.date(), time(hour=self._hour_dt.hour)
        ).isoformat()

    def set_power_watts(self, power_watts: int) -> None:
        """Set the power level for the hour, will be 0 if not set
        power_watts - (W) Negative value = charge (consuming), positive = discharge (producing)
        """
        self._power_watts = power_watts

    def get_power_watts(self) -> int:
        """Get the power level for the hour, will be 0 if not previously set
        Return power (W) Negative value = charge (consuming), positive = discharge (producing)
        """
        return self._power_watts

    def set_import_price(self, price: float):
        """Set the electricity import price for this hour"""
        self._import_price = price

    def get_import_price(self) -> float:
        """Get the electricity import price for this hour"""
        return self._import_price

    def set_export_price(self, price: float):
        """Set the electricity export price for this hour"""
        self._export_price = price

    def get_export_price(self) -> float:
        """Get the electricity export price for this hour"""
        return self._export_price

    def get_active_price(self) -> float:
        """Returns import price if power is set to charge, export price if set to discharge"""
        if self._power_watts > 0:
            return self._export_price
        else:
            return self._import_price

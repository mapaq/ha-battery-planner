"""Interface for a battery API to be used by BatteryPlanner"""

from abc import ABC, abstractmethod
from .charge_plan import ChargePlan


class BatteryApiInterface(ABC):
    """Abstract class that defines the interface for a battery scheduler"""

    @classmethod
    @abstractmethod
    def __init__(cls, secrets_json: dict[str:str]):
        """Constructor taking secrets data as a json dict"""

    @classmethod
    @abstractmethod
    async def login(cls) -> bool:
        """Login to the scheduling service
        Return True if login was successful"""

    @classmethod
    @abstractmethod
    async def schedule_battery(cls, new_charge_plan: ChargePlan) -> bool:
        """Create new schedule
        Return True if the scheduling was successful"""

    @classmethod
    @abstractmethod
    async def get_active_charge_plan(cls) -> ChargePlan:
        """Return the active charge plan, None if the request failed"""

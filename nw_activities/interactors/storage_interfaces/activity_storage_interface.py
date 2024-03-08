import abc
import datetime
from dataclasses import dataclass
from typing import Optional, List

from nw_activities.interactors.dtos import UserActivityDTO


@dataclass
class ActivityDTO:
    name_enum: str
    name: str
    description: Optional[str]


class ActivityStorageInterface(abc.ABC):

    @abc.abstractmethod
    def is_valid_activity(self, activity_name_enum: str) -> bool:
        pass

    @abc.abstractmethod
    def create_user_activity_log(self, user_activity_dto: UserActivityDTO):
        pass

    @abc.abstractmethod
    def create_activities(self, activity_dtos: List[ActivityDTO]):
        pass

    @abc.abstractmethod
    def get_existing_activity_name_enums(
            self, activity_name_enums: List[str]) -> List[str]:
        pass

    @abc.abstractmethod
    def get_user_activities(
            self, user_id: str, from_datetime: datetime.datetime,
            to_datetime: datetime.datetime) -> List[UserActivityDTO]:
        pass

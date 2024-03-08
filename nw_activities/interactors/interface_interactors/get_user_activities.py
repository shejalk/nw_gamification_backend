import datetime
from typing import List

from nw_activities.interactors.dtos import UserActivityDTO
from nw_activities.interactors.storage_interfaces\
    .activity_group_storage_interface import \
    ActivityGroupStorageInterface, UserActivityGroupStreakDTO
from nw_activities.interactors.storage_interfaces.activity_storage_interface \
    import ActivityStorageInterface


class GetUserActivityInteractor:

    def __init__(self, activity_storage: ActivityStorageInterface,
                 activity_group_storage: ActivityGroupStorageInterface):
        self.activity_storage = activity_storage
        self.activity_group_storage = activity_group_storage

    def get_user_activities(
            self, user_id: str, from_datetime: datetime.datetime,
            to_datetime: datetime.datetime) -> List[UserActivityDTO]:
        user_activities = self.activity_storage.get_user_activities(
            user_id, from_datetime, to_datetime)
        return user_activities

    def get_user_activity_group_streak_details(self, user_id: str) -> \
            List[UserActivityGroupStreakDTO]:
        user_activity_group_streak_dtos = \
            self.activity_group_storage.get_user_activity_group_streak_details(
                user_id)
        return user_activity_group_streak_dtos

    def get_user_activity_group_streak_details_with_transaction(
            self, user_id: str) -> List[UserActivityGroupStreakDTO]:
        user_activity_group_streak_dtos = \
            self.activity_group_storage\
            .get_user_activity_group_streak_details_with_transaction(user_id)
        return user_activity_group_streak_dtos

    def get_max_streak_for_user_ids(self, user_ids: List[str]) -> int:
        max_streak = self.activity_group_storage.get_max_streak_for_user_ids(
            user_ids)
        return max_streak

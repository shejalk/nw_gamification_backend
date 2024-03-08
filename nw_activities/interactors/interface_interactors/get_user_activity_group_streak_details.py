from typing import List

from nw_activities.interactors.storage_interfaces\
    .activity_group_storage_interface import \
    ActivityGroupStorageInterface, UserActivityGroupStreakDTO


class GetUserActivityGroupStreakDetails:
    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        self.activity_group_storage = activity_group_storage

    def get_user_activity_group_streaks_up_to_max_rank(
            self, user_ids: List[str], activity_group_ids: List[str],
            max_rank: int) -> List[UserActivityGroupStreakDTO]:

        user_activity_group_streak_dtos = self.activity_group_storage.\
            get_user_activity_group_streaks_up_to_max_rank(
                user_ids, activity_group_ids, max_rank)

        return user_activity_group_streak_dtos

    def get_user_activity_group_streak_for_given_streak(
            self, activity_group_ids: List[str], streak: int) -> \
            List[UserActivityGroupStreakDTO]:

        user_activity_group_streak_dtos = self.activity_group_storage.\
            get_user_activity_group_streak_for_given_streak(
                activity_group_ids, streak)

        return user_activity_group_streak_dtos

    def get_user_activity_group_streaks_for_user_ids(
            self, user_ids: List[str], activity_group_ids: List[str],
    ) -> List[UserActivityGroupStreakDTO]:

        user_activity_group_streak_dtos = self.activity_group_storage.\
            get_user_activity_group_streaks_for_user_ids(
                user_ids, activity_group_ids)

        return user_activity_group_streak_dtos

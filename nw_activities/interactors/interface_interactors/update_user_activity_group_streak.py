import datetime

from nw_activities.interactors.storage_interfaces\
    .activity_group_storage_interface import ActivityGroupStorageInterface


class UpdateUserActivityGroupStreak:

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        self.activity_group_storage = activity_group_storage

    def update_user_activity_group_streak_last_updated_at(
            self, user_id: str, last_updated_at: datetime.datetime):
        self.activity_group_storage. \
            update_user_activity_group_streak_last_updated_at(
                user_id, last_updated_at)

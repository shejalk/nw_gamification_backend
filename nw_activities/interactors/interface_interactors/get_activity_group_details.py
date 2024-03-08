from nw_activities.interactors.storage_interfaces.\
    activity_group_storage_interface import ActivityGroupStorageInterface


class GetActivityGroupDetailsInteractor:

    def __init__(self, storage: ActivityGroupStorageInterface):
        self.storage = storage

    def get_streak_enabled_activity_group_ids(self):
        return self.storage.get_streak_enabled_activity_group_ids()

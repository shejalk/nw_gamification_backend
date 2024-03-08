import abc

from nw_activities.constants.enum import FrequencyTypeEnum


class WebSocketServiceInterface(abc.ABC):

    @abc.abstractmethod
    def send_activity_group_completed_event(
            self, user_id: str, activity_group_id: str,
            frequency_type: FrequencyTypeEnum):
        pass

    @abc.abstractmethod
    def send_activity_group_streak_updated_event(
            self, user_id: str, activity_group_id: str,
            activity_group_streak: int):
        pass

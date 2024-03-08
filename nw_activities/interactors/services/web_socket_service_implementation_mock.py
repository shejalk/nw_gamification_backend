from typing import Union, Dict

from nw_activities.constants.enum import FrequencyTypeEnum
from nw_activities.interactors.services.web_socket_service_interface import \
    WebSocketServiceInterface


class WebSocketServiceImplementationMock(WebSocketServiceInterface):

    def send_activity_group_completed_event(
            self, user_id: str, activity_group_id: str,
            frequency_type: FrequencyTypeEnum):
        pass

    def send_activity_group_streak_updated_event(
            self, user_id: str, activity_group_id: str, weekday: str):
        pass

    def send_user_consistency_score_credited_event(
            self, user_id: str, streak_related_details_dict:
            Dict[str, Union[float, int]]):
        pass

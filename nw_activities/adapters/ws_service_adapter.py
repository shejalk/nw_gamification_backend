import logging
from typing import Dict, Union

from nw_activities.constants.enum import FrequencyTypeEnum
from nw_activities.interactors.services \
    .web_socket_service_implementation_mock import \
    WebSocketServiceImplementationMock
from nw_activities.utils.web_socket_utils.web_socket_service_implementation \
    import WebSocketServiceImplementation

logger = logging.getLogger(__name__)


class WebSocketServiceAdapter:

    @property
    def initialize_web_socket_service(self):
        from django.conf import settings
        if getattr(settings, "IS_WEB_SOCKET_ENABLED", False):
            return WebSocketServiceImplementation()
        return WebSocketServiceImplementationMock()

    def send_activity_group_completed_event(
            self, user_id: str, activity_group_id: str,
            frequency_type: FrequencyTypeEnum):
        self.initialize_web_socket_service.send_activity_group_completed_event(
            user_id, activity_group_id, frequency_type)

    def send_activity_group_streak_updated_event(
            self, user_id: str, activity_group_id: str, streak: int):
        self.initialize_web_socket_service\
            .send_activity_group_streak_updated_event(
                user_id, activity_group_id, streak)

    def send_user_consistency_score_credited_event(
            self, user_id: str, streak_related_details_dicts:
            Dict[str, Union[float, int]]):
        self.initialize_web_socket_service\
            .send_user_consistency_score_credited_event(
                user_id,streak_related_details_dicts)

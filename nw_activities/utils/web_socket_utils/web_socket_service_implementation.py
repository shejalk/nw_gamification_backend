import logging
from typing import List, Dict, Any, Union

from nw_activities.constants.enum import WebSocketActionEnum, \
    FrequencyTypeEnum
from nw_activities.interactors.services.web_socket_service_interface import \
    WebSocketServiceInterface

logger = logging.getLogger(__name__)

DEFAULT_SEQUENCE_NO_FOR_WS = 0


def exception_logger(func):
    def logger_method(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exception:
            print(exception)
            logger.warning('Web Socket Event Failed', extra={'stack': True})
    return logger_method


class WebSocketServiceImplementation(WebSocketServiceInterface):

    def send_activity_group_completed_event(
            self, user_id: str, activity_group_id: str,
            frequency_type: FrequencyTypeEnum):
        sequence_no = DEFAULT_SEQUENCE_NO_FOR_WS
        event_message = {
            "action": WebSocketActionEnum.ACTIVITY_GROUP_COMPLETED.value,
            "topic": user_id,
            "payload": {
                "user_id": user_id,
                "activity_group_id": activity_group_id,
                "frequency_type": frequency_type,
            },
            "sequence_no": sequence_no,
        }
        self.send_message_to_users(
            [user_id], event_message, sequence_no)

    def send_activity_group_streak_updated_event(
            self, user_id: str, activity_group_id: str,
            activity_group_streak: int):
        sequence_no = DEFAULT_SEQUENCE_NO_FOR_WS
        event_message = {
            "action": WebSocketActionEnum.ACTIVITY_GROUP_STREAK_UPDATED.value,
            "topic": user_id,
            "payload": {
                "user_id": user_id,
                "activity_group_id": activity_group_id,
                "streak_count": activity_group_streak,
            },
            "sequence_no": sequence_no,
        }
        self.send_message_to_users(
            [user_id], event_message, sequence_no)

    def send_user_consistency_score_credited_event(
            self, user_id: str, streak_related_details_dict:
            Dict[str, Union[float, int]]):
        sequence_no = DEFAULT_SEQUENCE_NO_FOR_WS
        payload = {
                "user_id": user_id,
                "previous_consistency_score":
                streak_related_details_dict["previous_consistency_score"],
                "credit_value": streak_related_details_dict["credit_value"],
                "streak": streak_related_details_dict["streak"],
            }
        event_message = {
            "action": WebSocketActionEnum.USER_CONSISTENCY_SCORE_CREDITED
            .value,
            "topic": user_id,
            "payload": payload,
            "sequence_no": sequence_no,
        }
        self.send_message_to_users(
            [user_id], event_message, sequence_no)

    @staticmethod
    @exception_logger
    def send_message_to_users(
            user_ids: List[str], event_message: Dict[str, Any],
            sequence_no: int):
        from ib_apigateway_ws.interfaces.ib_apigateway_ws_service_interface \
            import IBApigatewayWSServiceInterface
        service = IBApigatewayWSServiceInterface(user=None, access_token=None)
        service.send_message_to_users(user_ids, event_message, sequence_no)

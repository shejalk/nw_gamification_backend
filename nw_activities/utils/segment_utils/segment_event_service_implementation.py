from typing import Dict, Any, Optional
import logging
import analytics

from nw_activities.interactors.services.events_service_interface import \
    EventsServiceInterface

logger = logging.getLogger(__name__)


def exception_logger(func):
    def logger_method(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            logger.warning(
                f'Segment Events Emission Failed -> {func.__name__}',
                extra={'stack': True})

    return logger_method


class SegmentEventsServiceImplementation(EventsServiceInterface):
    def send_activity_group_streak_updated_event(
            self, user_id: str, streak: int):
        properties = {
            "latest_learning_streak": streak,
        }
        integrations = self._get_only_webengage_integrations_data()
        self.identify(user_id, properties, integrations)
        self.track_event(user_id, "User Streak Updated", properties,
                         integrations)

    def send_user_consistency_score_updated_event(
            self, user_id: str, latest_consistency_score: float):
        properties = {
            "latest_consistency_score": latest_consistency_score,
        }
        integrations = self._get_only_webengage_integrations_data()
        self.identify(user_id, properties, integrations)
        self.track_event(user_id, "User Consistency Score Updated", {},
                         integrations)

    @staticmethod
    @exception_logger
    def identify(user_id: str, properties: Dict[str, Any], integrations=None):
        if not integrations:
            integrations = {'all': True}
        analytics.identify(user_id, properties, integrations=integrations)

    @staticmethod
    @exception_logger
    def track_event(user_id: str, event: str, properties: Dict[str, Any],
                    integrations: Optional[Dict[str, bool]] = None):
        if not integrations:
            integrations = {'all': True}
        analytics.track(user_id, event, properties, integrations=integrations)
        analytics.flush()

    @staticmethod
    def _get_only_webengage_integrations_data():
        integrations = {
            'all': False,
            'WebEngage': True,
        }
        return integrations

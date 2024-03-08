
from nw_activities.interactors.services\
    .events_service_implementation_mock import EventsServiceImplementationMock


class EventsServiceAdapter:

    @property
    def event_service(self):
        from django.conf import settings
        if getattr(settings, "IS_SEGMENT_EVENTS_ENABLED", False):
            from nw_activities.utils.segment_utils\
                .segment_event_service_implementation import \
                SegmentEventsServiceImplementation
            return SegmentEventsServiceImplementation()
        return EventsServiceImplementationMock()

    def send_activity_group_streak_updated_event(
            self, user_id: str, streak: int):
        self.event_service.send_activity_group_streak_updated_event(
            user_id, streak)

    def send_user_consistency_score_updated_event(
            self, user_id: str, latest_consistency_score: float):
        self.event_service.send_user_consistency_score_updated_event(
            user_id, latest_consistency_score)

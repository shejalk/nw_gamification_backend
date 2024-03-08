from nw_activities.interactors.services.events_service_interface import \
    EventsServiceInterface


class EventsServiceImplementationMock(EventsServiceInterface):
    def send_activity_group_streak_updated_event(
            self, user_id: str, streak: int):
        pass

    def send_user_consistency_score_updated_event(
            self, user_id: str, latest_consistency_score: float):
        pass

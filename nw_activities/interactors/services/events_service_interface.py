import abc


class EventsServiceInterface(abc.ABC):

    @abc.abstractmethod
    def send_activity_group_streak_updated_event(
            self, user_id: str, streak: int):
        pass

    @abc.abstractmethod
    def send_user_consistency_score_updated_event(
            self, user_id: str, latest_consistency_score: float):
        pass

import datetime
from typing import List, Optional

from nw_activities.adapters.gamification_wrapper_service.gamification_wrapper \
    import UserActivityGroupEnabledDTO


class GamificationWrapperServiceAdapterMock:

    def is_activity_groups_enabled_for_users(self, user_ids: List[str]) -> \
            List[UserActivityGroupEnabledDTO]:
        return [
            UserActivityGroupEnabledDTO(
                user_id=user_id,
                activity_group_enabled=True,
            )
            for user_id in user_ids
        ]

    def is_user_has_access_to_perform_activities(self, user_id: str) -> bool:
        return True

    def is_streak_enabled(self, user_id: str) -> bool:
        return True

    def get_user_activity_group_instance_type(
            self, user_id: str, date: datetime.date) -> Optional[str]:
        return None

    def get_maximum_number_of_streak_freezes_allowed_per_month(self) -> int:
        return 3

    def update_leaderboard_for_streak_change(
            self, user_id: str, score_change: float,
            instance_datetime: datetime = None):
        return None

import datetime
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class UserActivityGroupEnabledDTO:
    user_id: str
    activity_group_enabled: bool


class GamificationWrapperServiceAdapter:

    @property
    def interface(self):
        from nkb_gamification_wrapper.app_interfaces.service_interface import \
            ServiceInterface
        return ServiceInterface()

    def is_activity_groups_enabled_for_users(self, user_ids: List[str]) -> \
            List[UserActivityGroupEnabledDTO]:
        user_onboard_step_completion_details_dtos = \
            self.interface.get_user_daily_goal_onboard_step_completion_details(
                user_ids)
        user_activity_enabled_dtos = [
            UserActivityGroupEnabledDTO(
                user_id=dto.user_id,
                activity_group_enabled=dto.is_completed,
            )
            for dto in user_onboard_step_completion_details_dtos
        ]
        return user_activity_enabled_dtos

    def is_user_has_access_to_perform_activities(self, user_id: str) -> bool:
        return self.interface.is_user_has_gamification_access(user_id)

    def is_streak_enabled(self, user_id: str) -> bool:
        return self.interface.is_streak_enabled(user_id)

    def get_user_activity_group_instance_type(
            self, user_id: str, date: datetime.date) -> Optional[str]:

        return self.interface.get_user_activity_group_instance_type(
            user_id, date)

    def get_maximum_number_of_streak_freezes_allowed_per_month(self) -> int:
        return self.interface. \
                get_maximum_number_of_streak_freezes_allowed_per_month()

    def update_leaderboard_for_streak_change(
            self, user_id: str, score_change: float,
            instance_datetime: datetime = None):
        self.interface.update_leaderboard_for_streak_change(
            user_id, score_change, instance_datetime)

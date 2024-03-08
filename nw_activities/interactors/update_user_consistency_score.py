from typing import List

from nw_activities.adapters.service_adapter import get_service_adapter
from nw_activities.adapters.resources_service_adapter import \
    UpdateUserResourceDTO
from nw_activities.constants.constants import ACTIVITY_ID_FOR_MANUAL_UPDATION
from nw_activities.constants.enum import ResourceNameEnum, TransactionTypeEnum
from nw_activities.exceptions.custom_exceptions import \
    UserDoesNotHaveGamificationAccess


class UpdateUserConsistencyScoreInteractor:
    def update_user_consistency_score(self, user_id: str, resource_value: int):
        if not self._is_valid_user(user_id):
            raise UserDoesNotHaveGamificationAccess

        self._update_users_resources_with_transaction(user_id, resource_value)

    @staticmethod
    def _is_valid_user(user_id: str) -> bool:
        adapter = get_service_adapter()
        return adapter.gamification_wrapper.is_streak_enabled(user_id)

    def _update_users_resources_with_transaction(
            self, user_id: str, resource_value: int):

        resource_name_enum = ResourceNameEnum.CONSISTENCY_SCORE.value
        activity_id = ACTIVITY_ID_FOR_MANUAL_UPDATION
        if resource_value > 0:
            transaction_type = TransactionTypeEnum.CREDIT.value
        else:
            transaction_type = TransactionTypeEnum.DEBIT.value

        update_dto = UpdateUserResourceDTO(
            user_id=user_id,
            activity_id=activity_id,
            name_enum=resource_name_enum,
            value=abs(resource_value),
            transaction_type=transaction_type,
            entity_id=None,
            entity_type=None,
        )

        self.update_user_resource([update_dto])

    @staticmethod
    def update_user_resource(update_dtos: List[UpdateUserResourceDTO]):
        adapter = get_service_adapter()
        adapter.resources.update_user_resources(update_dtos)

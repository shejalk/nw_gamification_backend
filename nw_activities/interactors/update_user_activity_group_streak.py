from datetime import datetime
from typing import List, Dict, Optional, Tuple

from ib_common.date_time_utils.get_current_local_date_time import \
    get_current_local_date_time
from ib_common.decorators.atomic_transaction import atomic_transaction

from nw_activities.adapters.resources_service_adapter import \
    UpdateUserResourceDTO, UserResourceDTO
from nw_activities.adapters.service_adapter import get_service_adapter
from nw_activities.constants.enum import InstanceTypeEnum, ResourceNameEnum, \
    TransactionTypeEnum, ResourceEntityTypeEnum
from nw_activities.interactors.dtos import UserActivityDTO
from nw_activities.interactors.mixins.activity_group_association_mixin import \
    ActivityGroupAssociationMixin
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import \
    ActivityGroupStorageInterface, UserActivityGroupStreakDTO, \
    ActivityGroupOptionalMetricDTO, UserActivityGroupInstanceDTO


class UpdateUserActivityGroupStreakInteractor(ActivityGroupAssociationMixin):

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        super().__init__(activity_group_storage)
        self.activity_group_storage = activity_group_storage

    def update_user_activity_group_streak_based_on_activity(
            self, user_activity_dto: UserActivityDTO):
        activity_group_ids = self._get_activity_group_ids(
            user_activity_dto.activity_name_enum)
        self.update_user_activity_group_streak(
            user_activity_dto.user_id, activity_group_ids)

    def update_user_activity_group_streak(
            self, user_id: str, activity_group_ids: List[str],
            instance_datetime: datetime = None):
        activity_group_frequency_config_dtos = \
            self.activity_group_storage.get_activity_groups_frequency_configs(
                activity_group_ids)

        user_activity_group_instance_dtos = \
            self.get_or_create_user_activity_group_instances(
                user_id, activity_group_ids,
                activity_group_frequency_config_dtos, instance_datetime)

        activity_group_id_wise_instance_dto = {
            dto.activity_group_id: dto
            for dto in user_activity_group_instance_dtos
        }
        activity_group_ids_to_update_streak = \
            list(activity_group_id_wise_instance_dto.keys())

        activity_group_id_wise_streak = \
            self.update_or_create_user_activity_group_streak(
                user_id, activity_group_ids_to_update_streak,
                activity_group_id_wise_instance_dto, instance_datetime)

        if not activity_group_id_wise_streak:
            return

        activity_group_id_wise_optional_metric_dtos = \
            self.get_activity_group_id_wise_optional_metric_dtos(
                activity_group_ids)

        activity_group_id_wise_resource_value, user_resource_dtos = \
            self.update_consistency_score_user_resource(
                activity_group_id_wise_streak, user_id,
                activity_group_id_wise_instance_dto)

        for activity_group_id in activity_group_ids_to_update_streak:
            optional_metric_dtos = \
                activity_group_id_wise_optional_metric_dtos[activity_group_id]
            activity_group_optional_metric_dtos = {
                activity_group_id: optional_metric_dtos
            }
            resource_value = activity_group_id_wise_resource_value.get(
                activity_group_id, 0.0)
            activity_group_id_instance_dto = \
                activity_group_id_wise_instance_dto[activity_group_id]
            self._update_user_activity_group_instance_optional_metrics(
                activity_group_optional_metric_dtos,
                ResourceNameEnum.consistency_score.value, resource_value,
                [activity_group_id_instance_dto])

        self._send_user_activity_group_streak_updated_event(
            user_id, activity_group_id_wise_streak)
        self._send_user_consistency_score_updated_event(
            user_id, user_resource_dtos)

    @atomic_transaction()
    def update_consistency_score_user_resource(
            self, activity_group_id_wise_streak: Dict[str, int], user_id: str,
            activity_group_id_wise_instance_dto:
            Dict[str, UserActivityGroupInstanceDTO]
    ) -> Tuple[Dict[str, float], List[UserResourceDTO]]:
        user_resource_dto = self._get_user_resource(
            user_id, ResourceNameEnum.consistency_score.value)
        resource_value = user_resource_dto.final_value if user_resource_dto \
            else 0

        update_user_resource_dtos = []
        activity_group_id_wise_resource_value = {}
        for activity_group_id, current_streak in \
                activity_group_id_wise_streak.items():
            current_value = current_streak
            if current_streak < 0:
                if resource_value <= 0:
                    current_value = 0
                else:
                    updated_value = resource_value + current_streak
                    if updated_value < 0:
                        current_value = current_streak - updated_value
                        resource_value -= current_value

            transaction_type = TransactionTypeEnum.credit.value
            if current_value < 0:
                transaction_type = TransactionTypeEnum.debit.value

            user_activity_group_instance_dto = \
                activity_group_id_wise_instance_dto[activity_group_id]

            update_user_resource_dtos.append(
                UpdateUserResourceDTO(
                    user_id=user_id,
                    activity_id=None,
                    name_enum=ResourceNameEnum.consistency_score.value,
                    value=abs(current_value),
                    transaction_type=transaction_type,
                    entity_id=user_activity_group_instance_dto.id,
                    entity_type=ResourceEntityTypeEnum
                    .user_activity_group_instance.value
                )
            )

            activity_group_id_wise_resource_value[activity_group_id] = \
                current_value

        adapter = get_service_adapter()

        user_resource_dtos = []
        if user_resource_dto:
            user_resource_dtos = [user_resource_dto]

        final_user_resource_dtos = \
            adapter.resources.update_user_resource_with_transaction(
                update_user_resource_dtos, user_resource_dtos)

        return activity_group_id_wise_resource_value, final_user_resource_dtos

    def _get_activity_group_ids(self, activity_id: str) -> List[str]:
        activity_group_association_dtos = self.activity_group_storage.\
            get_activity_group_associations_for_association_ids([activity_id])
        activity_group_ids = [
            dto.activity_group_id
            for dto in activity_group_association_dtos
        ]
        return activity_group_ids

    @atomic_transaction()
    def update_or_create_user_activity_group_streak(
            self, user_id: str, activity_group_ids: List[str],
            activity_group_id_wise_instance_dto:
            Dict[str, UserActivityGroupInstanceDTO],
            instance_datetime: datetime = None
    ) -> Dict[str, int]:
        user_activity_group_streak_dtos = self.activity_group_storage\
            .get_user_activity_group_streaks(user_id, activity_group_ids)

        if not instance_datetime:
            instance_datetime = get_current_local_date_time()
        instance_date = instance_datetime.date()

        existing_activity_group_ids = [
            dto.activity_group_id
            for dto in user_activity_group_streak_dtos
        ]
        activity_group_ids_streak_to_create = [
            activity_group_id
            for activity_group_id in activity_group_ids
            if activity_group_id not in existing_activity_group_ids
        ]

        activity_group_id_wise_streak = {}
        user_activity_group_streak_dtos_to_update = []
        for dto in user_activity_group_streak_dtos:
            if dto.last_updated_at.date() >= instance_date:
                continue

            instance_type = activity_group_id_wise_instance_dto[
                dto.activity_group_id].instance_type
            should_update_last_updated_at = False
            if instance_type not in [InstanceTypeEnum.paused.value,
                                     InstanceTypeEnum.leisure.value,
                                     InstanceTypeEnum.no_activity.value]:
                if dto.streak_count > 0:
                    dto.streak_count += 1
                else:
                    dto.streak_count = 1

                should_update_last_updated_at = True

            if instance_type in [InstanceTypeEnum.no_activity.value]:
                if dto.streak_count > 0:
                    dto.streak_count = 0
                else:
                    dto.streak_count -= 1

                should_update_last_updated_at = True

            if dto.streak_count > dto.max_streak_count:
                dto.max_streak_count = dto.streak_count

            if should_update_last_updated_at:
                dto.last_updated_at = instance_datetime
                user_activity_group_streak_dtos_to_update.append(dto)
                activity_group_id_wise_streak[dto.activity_group_id] = \
                    dto.streak_count

        from nw_activities.utils.generate_uuid import generate_uuid
        user_activity_group_streak_dtos_to_create = []
        for activity_group_id in activity_group_ids_streak_to_create:
            instance_type = activity_group_id_wise_instance_dto[
                activity_group_id].instance_type

            streak_count = 1
            max_streak_count = 1
            if instance_type in [InstanceTypeEnum.paused.value,
                                 InstanceTypeEnum.leisure.value,
                                 InstanceTypeEnum.no_activity.value]:
                streak_count = 0
                max_streak_count = 0

            user_activity_group_streak_dto = UserActivityGroupStreakDTO(
                user_id=user_id,
                streak_count=streak_count,
                max_streak_count=max_streak_count,
                id=generate_uuid(),
                activity_group_id=activity_group_id,
                last_updated_at=instance_datetime
            )
            user_activity_group_streak_dtos_to_create.append(
                user_activity_group_streak_dto)
            activity_group_id_wise_streak[
                user_activity_group_streak_dto.activity_group_id] = \
                user_activity_group_streak_dto.streak_count

        if user_activity_group_streak_dtos_to_create:
            self.activity_group_storage.create_user_activity_groups_streak(
                user_activity_group_streak_dtos_to_create)

        if user_activity_group_streak_dtos_to_update:
            self.activity_group_storage.update_user_activity_groups_streak(
                user_activity_group_streak_dtos_to_update)

        return activity_group_id_wise_streak

    def _update_user_activity_group_instance_optional_metrics(
            self, activity_group_id_wise_optional_metric_dtos:
            Dict[str, List[ActivityGroupOptionalMetricDTO]],
            resource_name_enum: str, resource_value: float,
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO]
    ):
        from nw_activities.interactors.update_activity_group_optional_metrics.\
            activity import ActivityGroupAssociationActivityInteractor
        interactor = ActivityGroupAssociationActivityInteractor(
            self.activity_group_storage)
        interactor.update_activity_groups_optional_metrics(
            activity_group_id_wise_optional_metric_dtos
            =activity_group_id_wise_optional_metric_dtos,
            entity_id=resource_name_enum,
            entity_value=resource_value,
            user_activity_group_instance_dtos=user_activity_group_instance_dtos)

    @staticmethod
    def _get_user_resource(user_id: str, resource_name_enum: str) -> \
            Optional[UserResourceDTO]:
        adapter = get_service_adapter()
        user_resource_dto = adapter.resources.get_user_resource(
            user_id, resource_name_enum)
        return user_resource_dto

    @staticmethod
    def _send_user_activity_group_streak_updated_event(
            user_id: str, activity_group_id_wise_streak: Dict[str, int]):
        adapter = get_service_adapter()
        for activity_group_id, streak in activity_group_id_wise_streak.items():
            adapter.event_service.send_activity_group_streak_updated_event(
                user_id, streak)
            if streak > 0:
                adapter.ws_service.send_activity_group_streak_updated_event(
                    user_id, activity_group_id, streak)

    @staticmethod
    def _send_user_consistency_score_updated_event(
            user_id: str, user_resource_dtos: List[UserResourceDTO]):
        for user_resource_dto in user_resource_dtos:
            if user_resource_dto.resource_name_enum == \
                    ResourceNameEnum.consistency_score.value:
                adapter = get_service_adapter()
                adapter.event_service.send_user_consistency_score_updated_event(
                    user_id, user_resource_dto.final_value)

from collections import defaultdict
from typing import List, Dict, Tuple

from ib_common.decorators.atomic_transaction import atomic_transaction

from nw_activities.adapters.resources_service_adapter import \
    UpdateUserResourceDTO, RewardConfigCompleteDetailsDTO
from nw_activities.adapters.service_adapter import get_service_adapter
from nw_activities.constants.enum import \
    CompletionMetricEntityTypeEnum, RewardTypeEnum, OperatorEnum, \
    RewardEntityTypeEnum, TransactionTypeEnum
from nw_activities.interactors.mixins.common import CommonMixin
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import ActivityGroupStorageInterface, \
    ActivityGroupRewardConfigDTO, UserActivityGroupInstanceDTO, \
    UserActivityGroupInstanceMetricTrackerDTO, \
    UserActivityGroupInstanceRewardDTO, UserAGInstanceIdAGRewardConfigIdDTO


class CreateUserActivityGroupInstanceRewardInteractor(CommonMixin):

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        self.activity_group_storage = activity_group_storage

    def create_user_activity_group_instance_rewards(
            self, user_id: str, activity_group_ids: List[str]):
        activity_group_ids += self._get_activity_group_ids_recursively(
            activity_group_ids)

        activity_group_frequency_config_dtos = \
            self.activity_group_storage.get_activity_groups_frequency_configs(
                activity_group_ids)

        activity_group_instance_identifier_dtos = \
            self.get_activity_group_instance_identifier(
                activity_group_frequency_config_dtos)

        user_activity_group_instance_dtos = \
            self.activity_group_storage.get_user_activity_group_instances(
                user_id, activity_group_instance_identifier_dtos)

        activity_group_reward_config_dtos = \
            self.activity_group_storage.get_activity_group_reward_configs(
                activity_group_ids)

        activity_group_id_wise_activity_group_reward_config_dtos = \
            self._get_activity_group_id_wise_activity_group_reward_config_dtos(
                activity_group_reward_config_dtos)

        user_ag_instance_completion_metric_entity_type_wise_total_value = \
            self._get_user_ag_instance_completion_metric_entity_type_wise_total_value(
                activity_group_ids, user_activity_group_instance_dtos)

        user_ag_instance_id_reward_config_id_dtos = \
            self._get_user_ag_instance_id_reward_config_id_dtos(
                user_activity_group_instance_dtos,
                activity_group_id_wise_activity_group_reward_config_dtos)

        self._create_user_group_instance_rewards(
            activity_group_id_wise_activity_group_reward_config_dtos,
            user_ag_instance_completion_metric_entity_type_wise_total_value,
            user_id, user_ag_instance_id_reward_config_id_dtos,
            user_activity_group_instance_dtos,
            activity_group_reward_config_dtos)

    @atomic_transaction()
    def _create_user_group_instance_rewards(
            self,
            activity_group_id_wise_activity_group_reward_config_dtos:
            Dict[str, List[ActivityGroupRewardConfigDTO]],
            user_ag_instance_completion_metric_entity_type_wise_total_value:
            Dict[Tuple[str, CompletionMetricEntityTypeEnum], float],
            user_id: str,
            user_ag_instance_id_reward_config_id_dtos:
            List[UserAGInstanceIdAGRewardConfigIdDTO],
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO],
            activity_group_reward_config_dtos:
            List[ActivityGroupRewardConfigDTO],
    ):
        user_activity_group_instance_reward_dtos = self\
            .activity_group_storage. \
            get_latest_user_activity_group_instance_rewards_with_transaction(
                user_ag_instance_id_reward_config_id_dtos)

        user_ag_instance_id_ag_reward_config_id_wise_user_agi_reward_dto = {
            (dto.user_activity_group_instance_id,
             dto.activity_group_reward_config_id): dto
            for dto in user_activity_group_instance_reward_dtos
        }

        ag_id_wise_user_activity_group_instance_id = \
            self._get_activity_group_id_wise_user_activity_group_instance_id(
                user_activity_group_instance_dtos)

        resource_reward_config_id_wise_reward_config_dto = \
            self._get_resource_reward_config_id_wise_reward_config_dto(
                activity_group_reward_config_dtos)

        user_activity_group_instance_reward_dtos_to_create = []
        user_resources_dtos = []
        for activity_group_id, user_activity_group_instance_id in \
                ag_id_wise_user_activity_group_instance_id.items():
            activity_group_reward_config_dtos = \
                activity_group_id_wise_activity_group_reward_config_dtos[
                    activity_group_id]
            for dto in activity_group_reward_config_dtos:
                reward_config_dto = \
                    resource_reward_config_id_wise_reward_config_dto[
                        dto.resource_reward_config_id]

                current_value = \
                    self._user_ag_instance_completion_metric_current_value(
                        reward_config_dto, user_activity_group_instance_id,
                        user_ag_instance_completion_metric_entity_type_wise_total_value)

                user_ag_instance_reward_dto = \
                    user_ag_instance_id_ag_reward_config_id_wise_user_agi_reward_dto.get(
                        (user_activity_group_instance_id, dto.id),
                    )

                each_user_resources_dtos, \
                    each_user_activity_group_instance_reward_dtos_to_create = \
                    self._get_user_activity_group_instance_reward_dtos_and_user_resources(
                        current_value, dto, reward_config_dto,
                        user_ag_instance_reward_dto,
                        user_activity_group_instance_id, user_id)

                user_resources_dtos += each_user_resources_dtos
                user_activity_group_instance_reward_dtos_to_create += \
                    each_user_activity_group_instance_reward_dtos_to_create

        if user_resources_dtos:
            self._update_user_resources(user_resources_dtos)

        if user_activity_group_instance_reward_dtos_to_create:
            self.activity_group_storage.\
                create_user_activity_group_instance_rewards(
                    user_activity_group_instance_reward_dtos_to_create)

    @staticmethod
    def _prepare_user_activity_group_instance_reward_dto(
            current_value: float, activity_group_reward_config_id: str,
            user_activity_group_instance_id: str) -> \
            UserActivityGroupInstanceRewardDTO:
        from nw_activities.utils.generate_uuid import generate_uuid
        return UserActivityGroupInstanceRewardDTO(
            id=generate_uuid(),
            user_activity_group_instance_id=user_activity_group_instance_id,
            activity_group_reward_config_id=activity_group_reward_config_id,
            rewarded_at_value=current_value,
        )

    @staticmethod
    def _prepare_user_resource_dtos(
            resource_name_enum: str, transaction_type: TransactionTypeEnum,
            rewarded_value: float, user_activity_group_instance_id: str,
            user_id: str) -> UpdateUserResourceDTO:
        return UpdateUserResourceDTO(
            name_enum=resource_name_enum,
            user_id=user_id,
            value=rewarded_value,
            transaction_type=transaction_type,
            activity_id=None,
            entity_id=user_activity_group_instance_id,
            entity_type=
            RewardEntityTypeEnum.USER_ACTIVITY_GROUP_INSTANCE.value,
        )

    @staticmethod
    def _get_activity_group_id_wise_user_activity_group_instance_id(
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO]) -> Dict[str, str]:
        activity_group_id_wise_user_activity_group_instance_id = {
            dto.activity_group_id: dto.id
            for dto in user_activity_group_instance_dtos
        }
        return activity_group_id_wise_user_activity_group_instance_id

    def _get_user_ag_instance_completion_metric_entity_type_wise_total_value(
            self, activity_group_ids: List[str],
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO],
    ) -> Dict[Tuple[str, CompletionMetricEntityTypeEnum], float]:
        ag_completion_metric_id_wise_entity_type = \
            self._get_activity_group_completion_metric_id_wise_entity_type(
                activity_group_ids)

        user_activity_group_instance_ids = \
            self._get_user_activity_group_instance_ids(
                user_activity_group_instance_dtos)

        user_ag_instance_metric_tracker_dtos = \
            self._get_user_activity_group_instances_metric_tracker(
                user_activity_group_instance_ids)

        user_ag_instance_completion_metric_entity_type_wise_total_value = \
            defaultdict(float)
        for dto in user_ag_instance_metric_tracker_dtos:
            entity_type = ag_completion_metric_id_wise_entity_type.get(
                dto.activity_group_completion_metric_id)

            if not entity_type:
                continue

            user_ag_instance_completion_metric_entity_type_wise_total_value[
                (dto.user_activity_group_instance_id, entity_type)] += \
                dto.current_value

        return user_ag_instance_completion_metric_entity_type_wise_total_value

    @staticmethod
    def _get_activity_group_id_wise_activity_group_reward_config_dtos(
            activity_group_reward_config_dtos:
            List[ActivityGroupRewardConfigDTO],
    ) -> Dict[str, List[ActivityGroupRewardConfigDTO]]:
        activity_group_id_wise_activity_group_reward_config_dtos = \
            defaultdict(list)
        for dto in activity_group_reward_config_dtos:
            activity_group_id_wise_activity_group_reward_config_dtos[
                dto.activity_group_id].append(dto)
        return activity_group_id_wise_activity_group_reward_config_dtos

    def _get_resource_reward_config_id_wise_reward_config_dto(
            self, activity_group_reward_config_dtos:
            List[ActivityGroupRewardConfigDTO]) -> \
            Dict[str, RewardConfigCompleteDetailsDTO]:
        reward_config_details_dtos = self._get_reward_config_details_dtos(
            activity_group_reward_config_dtos)
        resource_reward_config_id_wise_reward_config_dto = {
            dto.reward_config_id: dto
            for dto in reward_config_details_dtos
        }
        return resource_reward_config_id_wise_reward_config_dto

    @staticmethod
    def _get_reward_config_details_dtos(
            activity_group_reward_config_dtos:
            List[ActivityGroupRewardConfigDTO],
    ) -> List[RewardConfigCompleteDetailsDTO]:
        resource_reward_config_ids = [
            dto.resource_reward_config_id
            for dto in activity_group_reward_config_dtos
        ]

        adapter = get_service_adapter()
        reward_config_details_dtos = \
            adapter.resources.get_reward_config_details(
                resource_reward_config_ids)

        return reward_config_details_dtos

    def _get_user_activity_group_instance_reward_dtos_and_user_resources(
            self, current_value: int,
            activity_group_reward_config_dto: ActivityGroupRewardConfigDTO,
            reward_config_dto: RewardConfigCompleteDetailsDTO,
            user_ag_instance_reward_dto: UserActivityGroupInstanceRewardDTO,
            user_activity_group_instance_id: str, user_id: str):

        last_rewarded_at_value = 0
        if user_ag_instance_reward_dto:
            last_rewarded_at_value = \
                user_ag_instance_reward_dto.rewarded_at_value

        reward_multiplication_factor = \
            self._get_reward_multiplication_factor(
                reward_config_dto, current_value,
                last_rewarded_at_value)

        user_resources_dtos = []
        user_activity_group_instance_reward_dtos_to_create = []
        for transaction in reward_config_dto.reward_transactions:
            rewarded_value = transaction.resource_value * \
                             reward_multiplication_factor

            if rewarded_value > 0:
                user_resources_dtos.append(
                    self._prepare_user_resource_dtos(
                        transaction.resource_name_enum,
                        transaction.transaction_type, rewarded_value,
                        user_activity_group_instance_id, user_id),
                )

                user_activity_group_instance_reward_dtos_to_create.append(
                    self._prepare_user_activity_group_instance_reward_dto(
                        current_value, activity_group_reward_config_dto.id,
                        user_activity_group_instance_id),
                )

        return user_resources_dtos, \
            user_activity_group_instance_reward_dtos_to_create

    @staticmethod
    def _user_ag_instance_completion_metric_current_value(
            reward_config_dto: RewardConfigCompleteDetailsDTO,
            user_activity_group_instance_id: str,
            user_ag_instance_completion_metric_entity_type_wise_total_value:
            Dict[Tuple[str, CompletionMetricEntityTypeEnum], float],
    ):
        current_value = 0
        if reward_config_dto.reward_type == \
                RewardTypeEnum.RESOURCE_BASED.value:
            current_value = \
                user_ag_instance_completion_metric_entity_type_wise_total_value[
                    (user_activity_group_instance_id,
                     CompletionMetricEntityTypeEnum.
                     RESOURCE.value)
                ]

        if reward_config_dto.reward_type == \
                RewardTypeEnum.COMPLETION_BASED.value:
            current_value = \
                user_ag_instance_completion_metric_entity_type_wise_total_value[
                    (user_activity_group_instance_id,
                     CompletionMetricEntityTypeEnum.
                     ACTIVITY_GROUP_ASSOCIATION.value)
                ]

        return current_value

    def _get_activity_group_ids_recursively(
            self, association_ids: List[str]) -> List[str]:
        activity_group_association_dtos = self.activity_group_storage.\
            get_activity_group_associations_for_association_ids(
                association_ids)

        all_activity_group_ids = []
        activity_group_ids = [dto.activity_group_id
                              for dto in activity_group_association_dtos]

        if activity_group_ids:
            all_activity_group_ids += activity_group_ids
            all_activity_group_ids += \
                self._get_activity_group_ids_recursively(activity_group_ids)

        return all_activity_group_ids

    def _get_activity_group_completion_metric_id_wise_entity_type(
            self, activity_group_ids: List[str],
    ) -> Dict[str, CompletionMetricEntityTypeEnum]:
        activity_group_completion_metric_dtos = \
            self.activity_group_storage.get_activity_groups_completion_metrics(
                activity_group_ids)

        ag_completion_metric_id_wise_entity_type = {
            dto.id: dto.entity_type
            for dto in activity_group_completion_metric_dtos
        }

        return ag_completion_metric_id_wise_entity_type

    @staticmethod
    def _get_user_activity_group_instance_ids(
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO]) -> List[str]:
        user_activity_group_instance_ids = [
            dto.id for dto in user_activity_group_instance_dtos
        ]
        return user_activity_group_instance_ids

    @staticmethod
    def _get_user_ag_instance_id_reward_config_id_dtos(
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO],
            activity_group_id_wise_activity_group_reward_config_dtos:
            Dict[str, List[ActivityGroupRewardConfigDTO]],
    ) -> List[UserAGInstanceIdAGRewardConfigIdDTO]:
        user_ag_instance_id_reward_config_id_dtos = []
        for dto in user_activity_group_instance_dtos:
            activity_group_reward_config_dtos = \
                activity_group_id_wise_activity_group_reward_config_dtos[
                    dto.activity_group_id]
            for each in activity_group_reward_config_dtos:
                user_ag_instance_id_reward_config_id_dtos.append(
                    UserAGInstanceIdAGRewardConfigIdDTO(
                        user_activity_group_instance_id=dto.id,
                        activity_group_reward_config_id=each.id,
                    ),
                )
        return user_ag_instance_id_reward_config_id_dtos

    def _get_user_activity_group_instances_metric_tracker(
            self, user_activity_group_instance_ids: List[str],
    ) -> List[UserActivityGroupInstanceMetricTrackerDTO]:
        user_ag_instance_metric_tracker_dtos = self.activity_group_storage. \
            get_user_activity_group_instances_metric_tracker_without_transaction(
                user_activity_group_instance_ids)
        return user_ag_instance_metric_tracker_dtos

    def _get_reward_multiplication_factor(
            self, reward_config: RewardConfigCompleteDetailsDTO,
            current_value: float, last_rewarded_at_value: float) -> float:
        multiplication_factor = 0
        if reward_config.operator == OperatorEnum.EQ.value:
            if current_value == reward_config.value and \
                    last_rewarded_at_value != reward_config.value:
                multiplication_factor = 1

        if reward_config.operator == OperatorEnum.GT.value:
            if current_value > reward_config.value:
                if not last_rewarded_at_value > reward_config.value:
                    multiplication_factor = 1

        if reward_config.operator == OperatorEnum.GTE.value:
            if current_value >= reward_config.value:
                if not last_rewarded_at_value >= reward_config.value:
                    multiplication_factor = 1

        if reward_config.operator == OperatorEnum.BETWEEN.value:
            if reward_config.min_value <= current_value <= \
                    reward_config.max_value and not \
                    reward_config.min_value <= last_rewarded_at_value <= \
                    reward_config.max_value:
                multiplication_factor = 1

        if reward_config.operator == OperatorEnum.STEP.value:
            multiplication_factor = self._get_step_multiplication_factor(
                reward_config, current_value, last_rewarded_at_value)

        return multiplication_factor

    @staticmethod
    def _update_user_resources(
            user_resources_dtos: List[UpdateUserResourceDTO]):
        adapter = get_service_adapter()
        adapter.resources.update_user_resources(user_resources_dtos)

    @staticmethod
    def _get_step_multiplication_factor(
            reward_config: RewardConfigCompleteDetailsDTO,
            current_value: float, last_rewarded_at_value: float) -> float:
        multiplication_factor = 0
        if current_value > reward_config.min_value:
            is_eligible_for_reward = False
            last_rewarded_at_value = last_rewarded_at_value \
                if last_rewarded_at_value else reward_config.min_value

            next_reward_value = (
                    ((last_rewarded_at_value // reward_config.value) + 1) *
                    reward_config.value
            )
            if reward_config.max_value:
                if next_reward_value <= current_value <= \
                        reward_config.max_value:
                    is_eligible_for_reward = True
            else:
                if current_value >= next_reward_value:
                    is_eligible_for_reward = True

            if is_eligible_for_reward:
                multiplication_factor = \
                    (current_value // reward_config.value) - (
                            last_rewarded_at_value // reward_config.value)

        return multiplication_factor

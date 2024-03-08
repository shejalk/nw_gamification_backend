from collections import defaultdict
from typing import List, Dict

from nw_activities.adapters.resources_service_adapter import \
    RewardConfigCompleteDetailsDTO
from nw_activities.adapters.service_adapter import get_service_adapter
from nw_activities.constants.enum import RewardTypeEnum
from nw_activities.interactors.dtos import ActivityGroupIdRewardTypeDTO, \
    UserActivityGroupRewardDetailsDTO, RewardResourceDetailsDTO
from nw_activities.interactors.mixins.common import CommonMixin
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import \
    ActivityGroupStorageInterface, ActivityGroupRewardConfigDTO, \
    UserActivityGroupInstanceDTO, UserActivityGroupInstanceRewardDTO, \
    UserAGInstanceIdAGRewardConfigIdDTO


class GetUserActivityGroupRewardDetailsInteractor(CommonMixin):

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        self.activity_group_storage = activity_group_storage

    def get_user_activity_group_reward_details(
            self, user_id: str, activity_group_reward_type_dtos:
            List[ActivityGroupIdRewardTypeDTO]) -> \
            List[UserActivityGroupRewardDetailsDTO]:
        activity_group_id_wise_reward_types = \
            self._get_activity_group_id_wise_reward_types(
                activity_group_reward_type_dtos)

        activity_group_ids = list(activity_group_id_wise_reward_types.keys())

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

        resource_reward_config_id_wise_reward_config_dto = \
            self._get_resource_reward_config_id_wise_reward_config_dto(
                activity_group_reward_config_dtos)

        activity_group_id_wise_activity_group_reward_config_dtos = \
            self._get_activity_group_id_wise_activity_group_reward_config_dtos(
                activity_group_reward_config_dtos,
                resource_reward_config_id_wise_reward_config_dto,
                activity_group_id_wise_reward_types)

        user_ag_instance_id_reward_config_id_dtos = \
            self._get_user_ag_instance_id_reward_config_id_dtos(
                user_activity_group_instance_dtos,
                activity_group_id_wise_activity_group_reward_config_dtos)

        user_activity_group_instance_reward_dtos = \
            self.activity_group_storage.\
            get_latest_user_activity_group_instance_rewards(
                user_ag_instance_id_reward_config_id_dtos)

        user_activity_group_reward_details_dtos = \
            self._get_user_activity_group_reward_details_dtos(
                activity_group_id_wise_activity_group_reward_config_dtos,
                resource_reward_config_id_wise_reward_config_dto,
                user_activity_group_instance_dtos,
                user_activity_group_instance_reward_dtos)

        return user_activity_group_reward_details_dtos

    def _get_user_activity_group_reward_details_dtos(
            self, activity_group_id_wise_activity_group_reward_config_dtos,
            resource_reward_config_id_wise_reward_config_dto:
            Dict[str, RewardConfigCompleteDetailsDTO],
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO],
            user_activity_group_instance_reward_dtos:
            List[UserActivityGroupInstanceRewardDTO],
    ) -> List[UserActivityGroupRewardDetailsDTO]:
        ag_id_wise_user_ag_instance_id = \
            self._get_activity_group_id_wise_user_activity_group_instance_id(
                user_activity_group_instance_dtos)

        user_ag_instance_id_wise_ag_reward_config_ids = \
            self._get_user_ag_instance_id_wise_ag_reward_config_ids(
                user_activity_group_instance_reward_dtos)

        user_activity_group_reward_details_dtos = []
        for activity_group_id, ag_reward_config_dtos in \
                activity_group_id_wise_activity_group_reward_config_dtos\
                .items():
            user_activity_group_instance_id = \
                ag_id_wise_user_ag_instance_id.get(activity_group_id)
            user_activity_group_reward_config_ids = \
                user_ag_instance_id_wise_ag_reward_config_ids.get(
                    user_activity_group_instance_id, [])
            for dto in ag_reward_config_dtos:
                reward_config_dto = \
                    resource_reward_config_id_wise_reward_config_dto[
                        dto.resource_reward_config_id]
                is_earned = dto.id in user_activity_group_reward_config_ids
                for transaction in reward_config_dto.reward_transactions:
                    user_activity_group_reward_details_dtos.append(
                        UserActivityGroupRewardDetailsDTO(
                            activity_group_id=activity_group_id,
                            reward_type=reward_config_dto.reward_type,
                            resource_details=RewardResourceDetailsDTO(
                                resource_value=transaction.resource_value,
                                resource_type=transaction.resource_name_enum,
                            ),
                            is_earned=is_earned,
                        ),
                    )

        return user_activity_group_reward_details_dtos

    @staticmethod
    def _get_activity_group_id_wise_user_activity_group_instance_id(
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO]) -> Dict[str, str]:
        ag_id_wise_user_ag_instance_id = {
            dto.activity_group_id: dto.id
            for dto in user_activity_group_instance_dtos
        }
        return ag_id_wise_user_ag_instance_id

    @staticmethod
    def _get_user_ag_instance_id_wise_ag_reward_config_ids(
            user_activity_group_instance_reward_dtos):
        user_ag_instance_id_wise_ag_reward_config_ids = defaultdict(list)
        for dto in user_activity_group_instance_reward_dtos:
            user_ag_instance_id_wise_ag_reward_config_ids[
                dto.user_activity_group_instance_id].append(
                dto.activity_group_reward_config_id)
        return user_ag_instance_id_wise_ag_reward_config_ids

    @staticmethod
    def _get_activity_group_id_wise_reward_types(
            activity_group_reward_type_dtos: List[ActivityGroupIdRewardTypeDTO],
    ) -> Dict[str, List[RewardTypeEnum]]:
        activity_group_id_wise_reward_types = defaultdict(list)
        for dto in activity_group_reward_type_dtos:
            activity_group_id_wise_reward_types[dto.activity_group_id].append(
                dto.reward_type)
        return activity_group_id_wise_reward_types

    @staticmethod
    def _get_activity_group_id_wise_activity_group_reward_config_dtos(
            activity_group_reward_config_dtos:
            List[ActivityGroupRewardConfigDTO],
            resource_reward_config_id_wise_reward_config_dto:
            Dict[str, RewardConfigCompleteDetailsDTO],
            activity_group_id_wise_reward_types: Dict[str, List[RewardTypeEnum]],
    ) -> Dict[str, List[ActivityGroupRewardConfigDTO]]:
        activity_group_id_wise_activity_group_reward_config_dtos = \
            defaultdict(list)
        for dto in activity_group_reward_config_dtos:
            reward_config_dto = \
                resource_reward_config_id_wise_reward_config_dto[
                    dto.resource_reward_config_id]
            reward_types = activity_group_id_wise_reward_types[
                dto.activity_group_id]
            for reward_type in reward_types:
                if reward_config_dto.reward_type == reward_type:
                    activity_group_id_wise_activity_group_reward_config_dtos[
                        dto.activity_group_id].append(dto)
        return activity_group_id_wise_activity_group_reward_config_dtos

    def _get_resource_reward_config_id_wise_reward_config_dto(
            self, activity_group_reward_config_dtos:
            List[ActivityGroupRewardConfigDTO],
    ) -> Dict[str, RewardConfigCompleteDetailsDTO]:
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

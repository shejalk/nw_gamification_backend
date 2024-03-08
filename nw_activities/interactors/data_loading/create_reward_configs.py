from typing import Dict, Any, List

from nw_activities.adapters.service_adapter import get_service_adapter
from nw_activities.exceptions.custom_exceptions import \
    InvalidInputDataException
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import ActivityGroupStorageInterface, \
    RewardConfigDTO


class CreateRewardConfigInteractor:

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        self.activity_group_storage = activity_group_storage

    def create_reward_configs(self, reward_configs: List[Dict[str, Any]]):
        """
        :param reward_configs: [{
            "id": string
            "resource_reward_config_id": string
        }]
        :type reward_configs: List[Dict[str, Any]]
        :return:
        :rtype:
        """
        self._validate_reward_configs(reward_configs)

        reward_config_dtos = [
            RewardConfigDTO(
                id=each['id'],
                resource_reward_config_id=each['resource_reward_config_id'],
            )
            for each in reward_configs
        ]

        self.activity_group_storage.create_reward_configs(reward_config_dtos)

    def _validate_reward_configs(self, reward_configs: List[Dict[str, Any]]):
        invalid_reward_config_ids = self._get_invalid_reward_config_ids(
            reward_configs)

        invalid_resource_reward_config_ids = \
            self._get_invalid_resource_reward_config_ids(reward_configs)

        invalid_data = {}
        if invalid_reward_config_ids:
            invalid_data['invalid_reward_config_ids'] = \
                invalid_reward_config_ids

        if invalid_resource_reward_config_ids:
            invalid_data['invalid_resource_reward_config_ids'] = \
                invalid_resource_reward_config_ids

        if invalid_data:
            raise InvalidInputDataException(invalid_data)

    def _get_invalid_reward_config_ids(
            self, reward_configs: List[Dict[str, Any]]) -> List[str]:
        reward_config_ids = [each['id'] for each in reward_configs]

        existing_reward_config_ids = \
            self.activity_group_storage.get_existing_reward_config_ids(
                reward_config_ids)

        invalid_reward_config_ids = list(
            set(reward_config_ids) & set(existing_reward_config_ids),
        )
        return invalid_reward_config_ids

    def _get_invalid_resource_reward_config_ids(
            self, reward_configs: List[Dict[str, Any]]) -> List[str]:
        resource_reward_config_ids = [
            each['resource_reward_config_id']
            for each in reward_configs
        ]

        existing_resource_reward_config_ids = \
            self._get_existing_resource_reward_config_ids(
                resource_reward_config_ids)

        invalid_resource_reward_config_ids = list(
            set(resource_reward_config_ids) -
            set(existing_resource_reward_config_ids),
        )
        return invalid_resource_reward_config_ids

    @staticmethod
    def _get_existing_resource_reward_config_ids(
            resource_reward_config_ids: List[str]) -> List[str]:
        adapter = get_service_adapter()
        return adapter.resources.get_existing_reward_config_ids(
            resource_reward_config_ids)

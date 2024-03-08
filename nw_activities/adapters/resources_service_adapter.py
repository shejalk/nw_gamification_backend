from dataclasses import dataclass
from typing import List, Optional

from nw_activities.constants.enum import TransactionTypeEnum, RewardTypeEnum


@dataclass
class RewardTransactionConfigDTO:
    reward_transaction_config_id: str
    transaction_type: TransactionTypeEnum
    resource_name_enum: str
    resource_value: float


@dataclass
class RewardConfigCompleteDetailsDTO:
    reward_config_id: str
    reward_type: RewardTypeEnum
    operator: str
    min_value: float
    max_value: float
    value: float
    reward_transactions: List[RewardTransactionConfigDTO]


@dataclass
class UpdateUserResourceDTO:
    name_enum: str
    user_id: str
    value: float
    transaction_type: TransactionTypeEnum
    activity_id: Optional[str]
    entity_id: Optional[str]
    entity_type: Optional[str]


@dataclass
class UserResourceDTO:
    user_resource_id: str
    final_value: float
    user_id: str
    resource_name_enum: str


class ResourceServiceAdapter:

    @property
    def interface(self):
        from nw_resources.app_interfaces.service_interface import \
            ServiceInterface
        return ServiceInterface()

    def get_reward_config_details(self, reward_config_ids: List[str]) -> \
            List[RewardConfigCompleteDetailsDTO]:
        reward_config_details_interface_dtos = \
            self.interface.get_reward_configs_details(reward_config_ids)

        reward_config_details_dtos = [
            RewardConfigCompleteDetailsDTO(
                reward_config_id=dto.reward_config_id,
                reward_type=dto.reward_type,
                operator=dto.operator,
                min_value=dto.min_value,
                max_value=dto.max_value,
                value=dto.value,
                reward_transactions=[
                    RewardTransactionConfigDTO(
                        reward_transaction_config_id=transaction
                        .reward_transaction_config_id,
                        transaction_type=transaction.transaction_type,
                        resource_name_enum=transaction.resource_name_enum,
                        resource_value=transaction.resource_value,
                    )
                    for transaction in dto.reward_transactions
                ],
            )
            for dto in reward_config_details_interface_dtos
        ]

        return reward_config_details_dtos

    def update_user_resources(
            self, user_resource_dtos: List[UpdateUserResourceDTO]):
        from nw_resources.app_interfaces.dtos import UpdateUserResourceDTO
        update_user_resource_interface_dtos = [
            UpdateUserResourceDTO(
                resource_name_enum=dto.name_enum,
                user_id=dto.user_id,
                value=dto.value,
                transaction_type=dto.transaction_type,
                activity_id=dto.activity_id,
                entity_id=dto.entity_id,
                entity_type=dto.entity_type,
            )
            for dto in user_resource_dtos
        ]
        self.interface.update_user_resources(
            update_user_resource_interface_dtos)

    def get_existing_reward_config_ids(
            self, resource_reward_config_ids: List[str]) -> List[str]:
        return self.interface.get_existing_reward_config_ids(
            resource_reward_config_ids)

    def get_existing_resource_name_enums(
            self, resource_name_enums: List[str]) -> List[str]:
        return self.interface.get_existing_resource_name_enums(
            resource_name_enums)

    def get_user_resource(self, user_id: str, resource_name_enum: str) -> \
            Optional[UserResourceDTO]:
        user_resource_interface_dto = \
            self.interface.get_user_resource(user_id, resource_name_enum)

        if not user_resource_interface_dto:
            return

        user_resource_dto = UserResourceDTO(
            user_id=user_resource_interface_dto.user_id,
            resource_name_enum=user_resource_interface_dto.resource_name_enum,
            final_value=user_resource_interface_dto.final_value,
            user_resource_id=user_resource_interface_dto.user_resource_id,
        )

        return user_resource_dto

    def update_user_resource_with_transaction(
            self, update_user_resource_dtos: List[UpdateUserResourceDTO],
            user_resource_dtos: List[UserResourceDTO]) -> List[UserResourceDTO]:
        from nw_resources.app_interfaces.dtos import UpdateUserResourceDTO as\
            UpdateUserResourceInterfaceDTO
        from nw_resources.interactors.storage_interfaces.dtos import \
            UserResourceDTO as UserResourceInterfaceDTO
        update_user_resource_interface_dtos = [
            UpdateUserResourceInterfaceDTO(
                resource_name_enum=dto.name_enum,
                user_id=dto.user_id,
                value=dto.value,
                transaction_type=dto.transaction_type,
                activity_id=dto.activity_id,
                entity_id=dto.entity_id,
                entity_type=dto.entity_type,
            )
            for dto in update_user_resource_dtos
        ]

        user_resource_interface_dtos = [
            UserResourceInterfaceDTO(
                user_id=dto.user_id,
                resource_name_enum=dto.resource_name_enum,
                final_value=dto.final_value,
                user_resource_id=dto.user_resource_id,
            )
            for dto in user_resource_dtos
        ]

        final_user_resource_interface_dtos = \
            self.interface.update_user_resource_with_transaction(
                update_user_resource_interface_dtos,
                user_resource_interface_dtos)

        final_user_resource_dtos = [
            UserResourceDTO(
                user_id=dto.user_id,
                resource_name_enum=dto.resource_name_enum,
                final_value=dto.final_value,
                user_resource_id=dto.user_resource_id,
            )
            for dto in final_user_resource_interface_dtos
        ]

        return final_user_resource_dtos

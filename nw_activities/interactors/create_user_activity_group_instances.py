import datetime
from typing import List, Dict, Tuple

from nw_activities.adapters.service_adapter import get_service_adapter
from nw_activities.constants.enum import FrequencyTypeEnum, \
    CompletionStatusEnum, InstanceTypeEnum
from nw_activities.exceptions.custom_exceptions import \
    InvalidInstanceTypesException
from nw_activities.interactors.dtos import UserInstanceTypeDTO
from nw_activities.interactors.mixins.common import CommonMixin
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import ActivityGroupStorageInterface, \
    ActivityGroupInstanceIdentifierDTO, UserActivityGroupInstanceDTO, \
    ActivityGroupFrequencyConfigDTO


class CreateUserActivityGroupInstanceInteractor(CommonMixin):

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        self.activity_group_storage = activity_group_storage

    def create_user_activity_group_instance_with_daily_frequency(
            self, user_instance_type_dtos: List[UserInstanceTypeDTO],
            instance_date: datetime.date = None):
        self._validate_user_instance_types(user_instance_type_dtos)

        filtered_user_instance_type_dtos = \
            self._filter_user_instance_types_based_on_ag_availability(
                user_instance_type_dtos)

        if not filtered_user_instance_type_dtos:
            return

        activity_group_ids = \
            self.activity_group_storage.get_all_activity_group_ids()
        streak_enabled_activity_group_ids = \
            self.activity_group_storage.get_streak_enabled_activity_group_ids()
        activity_group_ids = list(set(activity_group_ids) -
                                  set(streak_enabled_activity_group_ids))

        activity_group_frequency_config_dtos = \
            self.activity_group_storage.get_activity_groups_frequency_configs(
                activity_group_ids)

        daily_activity_group_frequency_config_dtos = \
            self._get_daily_activity_group_frequency_config_dtos(
                activity_group_frequency_config_dtos)

        activity_group_instance_identifier_dtos = \
            self.get_activity_group_instance_identifier(
                daily_activity_group_frequency_config_dtos, instance_date)

        user_ids = [dto.user_id for dto in user_instance_type_dtos]
        user_activity_group_instance_dtos = \
            self.activity_group_storage.get_users_activity_group_instances(
                user_ids, activity_group_instance_identifier_dtos)

        activity_group_id_wise_instance_identifier = \
            self._get_activity_group_id_wise_instance_identifier(
                activity_group_instance_identifier_dtos)

        user_id_activity_group_id_wise_user_activity_group_instance_dto = \
            self._get_user_id_ag_id_wise_user_activity_group_instance_dto(
                user_activity_group_instance_dtos)

        self._create_or_update_user_activity_group_instances(
            activity_group_id_wise_instance_identifier,
            user_id_activity_group_id_wise_user_activity_group_instance_dto,
            filtered_user_instance_type_dtos)

    def create_user_activity_group_streak_instance_with_daily_frequency(
            self, user_instance_type_dtos: List[UserInstanceTypeDTO],
            instance_date: datetime.date = None):
        self._validate_user_instance_types(user_instance_type_dtos)

        activity_group_ids = \
            self.activity_group_storage.get_streak_enabled_activity_group_ids()

        activity_group_frequency_config_dtos = \
            self.activity_group_storage.get_activity_groups_frequency_configs(
                activity_group_ids)

        daily_activity_group_frequency_config_dtos = \
            self._get_daily_activity_group_frequency_config_dtos(
                activity_group_frequency_config_dtos)

        activity_group_instance_identifier_dtos = \
            self.get_activity_group_instance_identifier(
                daily_activity_group_frequency_config_dtos, instance_date)

        user_ids = [dto.user_id for dto in user_instance_type_dtos]
        user_activity_group_instance_dtos = \
            self.activity_group_storage.get_users_activity_group_instances(
                user_ids, activity_group_instance_identifier_dtos)

        activity_group_id_wise_instance_identifier = \
            self._get_activity_group_id_wise_instance_identifier(
                activity_group_instance_identifier_dtos)

        user_id_activity_group_id_wise_user_activity_group_instance_dto = \
            self._get_user_id_ag_id_wise_user_activity_group_instance_dto(
                user_activity_group_instance_dtos)

        self._crud_user_activity_group_instances(
            activity_group_id_wise_instance_identifier,
            user_id_activity_group_id_wise_user_activity_group_instance_dto,
            user_instance_type_dtos)

    def delete_streak_users_activity_group_instances_with_daily_frequency(
            self, user_ids: List[str], instance_date: datetime.date):
        activity_group_ids = \
            self.activity_group_storage.get_streak_enabled_activity_group_ids()

        activity_group_frequency_config_dtos = \
            self.activity_group_storage.get_activity_groups_frequency_configs(
                activity_group_ids)

        daily_activity_group_frequency_config_dtos = \
            self._get_daily_activity_group_frequency_config_dtos(
                activity_group_frequency_config_dtos)

        activity_group_instance_identifier_dtos = \
            self.get_activity_group_instance_identifier(
                daily_activity_group_frequency_config_dtos, instance_date)

        user_activity_group_instance_dtos = \
            self.activity_group_storage.get_users_activity_group_instances(
                user_ids, activity_group_instance_identifier_dtos)

        self._delete_users_activity_group_instances(
            user_activity_group_instance_dtos)

    def _delete_users_activity_group_instances(
            self, user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO]):
        user_activity_group_instances_to_delete = [
            dto.id for dto in user_activity_group_instance_dtos
        ]
        if user_activity_group_instances_to_delete:
            self.activity_group_storage.delete_user_activity_group_instances(
                user_activity_group_instances_to_delete)

    def _crud_user_activity_group_instances(
            self, activity_group_id_wise_instance_identifier: Dict[str, str],
            user_id_ag_id_wise_user_activity_group_instance_dto:
            Dict[Tuple[str, str], UserActivityGroupInstanceDTO],
            user_instance_type_dtos: List[UserInstanceTypeDTO]):
        from nw_activities.utils.generate_uuid import generate_uuid
        user_activity_group_instances_to_update = []
        user_activity_group_instances_to_create = []
        user_activity_group_instances_to_delete = []
        for dto in user_instance_type_dtos:
            for activity_group_id, instance_identifier in \
                    activity_group_id_wise_instance_identifier.items():
                user_activity_group_instance_dto = \
                    user_id_ag_id_wise_user_activity_group_instance_dto.get(
                        (dto.user_id, activity_group_id))
                if user_activity_group_instance_dto:
                    if user_activity_group_instance_dto.instance_type == \
                            InstanceTypeEnum.PAUSED.value:
                        user_activity_group_instances_to_delete.append(
                            user_activity_group_instance_dto.id)
                    else:
                        user_activity_group_instance_dto.instance_type = \
                            dto.instance_type
                        user_activity_group_instances_to_update.append(
                            user_activity_group_instance_dto)
                else:
                    user_activity_group_instances_to_create.append(
                        UserActivityGroupInstanceDTO(
                            id=generate_uuid(),
                            user_id=dto.user_id,
                            instance_identifier=instance_identifier,
                            instance_type=dto.instance_type,
                            activity_group_id=activity_group_id,
                            completion_percentage=0.0,
                            completion_status=
                            CompletionStatusEnum.YET_TO_START.value,
                        ),
                    )

        if user_activity_group_instances_to_create:
            self.activity_group_storage.create_user_activity_group_instances(
                user_activity_group_instances_to_create)

        if user_activity_group_instances_to_update:
            self.activity_group_storage.update_user_activity_group_instances(
                user_activity_group_instances_to_update)

        if user_activity_group_instances_to_delete:
            self.activity_group_storage.delete_user_activity_group_instances(
                user_activity_group_instances_to_delete)

    def _create_or_update_user_activity_group_instances(
            self, activity_group_id_wise_instance_identifier: Dict[str, str],
            user_id_ag_id_wise_user_activity_group_instance_dto:
            Dict[Tuple[str, str], UserActivityGroupInstanceDTO],
            user_instance_type_dtos: List[UserInstanceTypeDTO]):
        from nw_activities.utils.generate_uuid import generate_uuid
        user_activity_group_instances_to_update = []
        user_activity_group_instances_to_create = []
        for dto in user_instance_type_dtos:
            for activity_group_id, instance_identifier in \
                    activity_group_id_wise_instance_identifier.items():
                user_activity_group_instance_dto = \
                    user_id_ag_id_wise_user_activity_group_instance_dto.get(
                        (dto.user_id, activity_group_id))
                if user_activity_group_instance_dto:
                    user_activity_group_instance_dto.instance_type = \
                        dto.instance_type
                    user_activity_group_instances_to_update.append(
                        user_activity_group_instance_dto)
                else:
                    user_activity_group_instances_to_create.append(
                        UserActivityGroupInstanceDTO(
                            id=generate_uuid(),
                            user_id=dto.user_id,
                            instance_identifier=instance_identifier,
                            instance_type=dto.instance_type,
                            activity_group_id=activity_group_id,
                            completion_percentage=0.0,
                            completion_status=CompletionStatusEnum.YET_TO_START.value,
                        ),
                    )

        if user_activity_group_instances_to_create:
            self.activity_group_storage.create_user_activity_group_instances(
                user_activity_group_instances_to_create)

        if user_activity_group_instances_to_update:
            self.activity_group_storage.update_user_activity_group_instances(
                user_activity_group_instances_to_update)

    @staticmethod
    def _get_user_id_ag_id_wise_user_activity_group_instance_dto(
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO]) -> \
            Dict[Tuple[str, str], UserActivityGroupInstanceDTO]:
        user_id_activity_group_id_wise_user_activity_group_instance_dto = {}
        for dto in user_activity_group_instance_dtos:
            user_id_activity_group_id_wise_user_activity_group_instance_dto[
                (dto.user_id, dto.activity_group_id)] = dto
        return user_id_activity_group_id_wise_user_activity_group_instance_dto

    @staticmethod
    def _get_daily_activity_group_frequency_config_dtos(
            activity_group_frequency_config_dtos:
            List[ActivityGroupFrequencyConfigDTO]) -> \
            List[ActivityGroupFrequencyConfigDTO]:
        daily_activity_group_frequency_config_dtos = [
            dto
            for dto in activity_group_frequency_config_dtos
            if dto.frequency_type == FrequencyTypeEnum.DAILY.value
        ]
        return daily_activity_group_frequency_config_dtos

    @staticmethod
    def _get_activity_group_id_wise_instance_identifier(
            activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO]) -> Dict[str, str]:
        activity_group_id_wise_instance_identifier = {
            dto.activity_group_id: dto.instance_identifier
            for dto in activity_group_instance_identifier_dtos
        }
        return activity_group_id_wise_instance_identifier

    @staticmethod
    def _validate_user_instance_types(
            user_instance_type_dtos: List[UserInstanceTypeDTO]):
        instance_types = [
            dto.instance_type
            for dto in user_instance_type_dtos
        ]

        invalid_instance_types = list(
            set(instance_types) -
            set(InstanceTypeEnum.get_list_of_values()),
        )

        if invalid_instance_types:
            raise InvalidInstanceTypesException(invalid_instance_types)

    @staticmethod
    def _filter_user_instance_types_based_on_ag_availability(
            user_instance_type_dtos: List[UserInstanceTypeDTO]) -> \
            List[UserInstanceTypeDTO]:
        adapter = get_service_adapter()

        user_ids = [
            dto.user_id
            for dto in user_instance_type_dtos
        ]

        user_activity_group_enabled_dtos = \
            adapter.gamification_wrapper.is_activity_groups_enabled_for_users(
                user_ids)

        activity_group_enabled_user_ids = [
            dto.user_id
            for dto in user_activity_group_enabled_dtos
            if dto.activity_group_enabled
        ]

        return [
            dto for dto in user_instance_type_dtos
            if dto.user_id in activity_group_enabled_user_ids
        ]

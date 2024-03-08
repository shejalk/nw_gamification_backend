import datetime
from collections import defaultdict
from typing import List, Dict, Tuple

from nw_activities.constants.enum import CompletionStatusEnum, \
    FrequencyTypeEnum, InstanceTypeEnum, ActivityGroupAssociationTypeEnum
from nw_activities.interactors.dtos import \
    UserActivityGroupInstanceWithAssociationDTO, ActivityGroupInstanceDTO
from nw_activities.interactors.mixins.common import CommonMixin
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import \
    ActivityGroupStorageInterface, ActivityGroupInstanceIdentifierDTO, \
    ActivityGroupAssociationDTO, UserActivityGroupInstanceDTO, \
    ActivityGroupFrequencyConfigDTO, UserActivityGroupInstanceWithDatetimeDTO


class GetUserActivityGroupInstanceInteractor(CommonMixin):

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        self.activity_group_storage = activity_group_storage

    def get_user_activity_group_instances(self, user_id: str) -> \
            List[UserActivityGroupInstanceWithAssociationDTO]:
        activity_group_ids = \
            self.activity_group_storage.get_all_activity_group_ids()
        streak_activity_group_ids = \
            self.activity_group_storage.get_streak_enabled_activity_group_ids()
        activity_group_ids = list(set(activity_group_ids) -
                                  set(streak_activity_group_ids))

        activity_group_association_dtos = self.activity_group_storage.\
            get_activity_group_associations_for_activity_group_ids(
                activity_group_ids)

        user_activity_group_instance_with_associations = \
            self.get_user_activity_group_instances_with_associations_instances(
                user_id, activity_group_association_dtos)

        return user_activity_group_instance_with_associations

    def get_agi_user_ids_for_instance_and_frequency_type(
            self, instance_type: InstanceTypeEnum,
            frequency_type: FrequencyTypeEnum) -> List[str]:
        activity_group_ids = \
            self.activity_group_storage.get_all_activity_group_ids()
        streak_activity_group_ids = \
            self.activity_group_storage.get_streak_enabled_activity_group_ids()
        activity_group_ids = list(set(activity_group_ids) -
                                  set(streak_activity_group_ids))

        activity_group_frequency_config_dtos = \
            self.activity_group_storage.get_activity_groups_frequency_configs(
                activity_group_ids)

        activity_group_frequency_config_dtos = [
            dto for dto in activity_group_frequency_config_dtos
            if dto.frequency_type == frequency_type
        ]

        activity_group_instance_identifier_dtos = \
            self.get_activity_group_instance_identifier(
                activity_group_frequency_config_dtos)

        user_ids = self.activity_group_storage\
            .get_activity_group_instance_user_ids_for_instance_type(
                activity_group_instance_identifier_dtos, instance_type)

        return user_ids

    def get_activity_group_instance_user_ids_for_date(
            self, activity_group_ids: List[str],
            instance_types: List[InstanceTypeEnum],
            instance_date: datetime.date, user_ids: List[str],
    ) -> List[str]:
        activity_group_frequency_config_dtos = \
            self.activity_group_storage.get_activity_groups_frequency_configs(
                activity_group_ids)

        activity_group_instance_identifier_dtos = \
            self.get_activity_group_instance_identifier(
                activity_group_frequency_config_dtos, instance_date)

        user_ids = self.activity_group_storage\
            .get_activity_group_instance_user_ids_for_instance_types(
                activity_group_instance_identifier_dtos, instance_types,
                user_ids)

        return user_ids

    def get_user_activity_group_instances_with_associations_instances(
            self, user_id: str,
            activity_group_association_dtos: List[ActivityGroupAssociationDTO],
    ) -> List[UserActivityGroupInstanceWithAssociationDTO]:
        activity_group_id_wise_association_ids = \
            self._get_activity_group_id_wise_association_ids(
                activity_group_association_dtos)

        activity_group_frequency_config_dtos, \
            activity_group_instance_identifier_dtos = \
            self._get_activity_groups_data(activity_group_association_dtos)

        activity_group_id_wise_frequency_type = \
            self._get_activity_group_id_wise_frequency_type(
                activity_group_frequency_config_dtos)

        activity_group_id_wise_instance_identifier = \
            self._get_activity_group_id_wise_instance_identifier(
                activity_group_instance_identifier_dtos)

        activity_group_id_association_id_wise_instance_identifiers = \
            self._get_activity_group_id_association_id_wise_instance_identifiers(
                activity_group_id_wise_instance_identifier,
                activity_group_id_wise_association_ids)

        user_specific_ag_instance_identifier_dtos = \
            self._get_user_specific_activity_group_instance_identifier_dtos(
                activity_group_id_wise_instance_identifier,
                activity_group_id_association_id_wise_instance_identifiers)

        user_activity_group_instance_dtos = \
            self.activity_group_storage.get_user_activity_group_instances(
                user_id, user_specific_ag_instance_identifier_dtos)

        ag_id_instance_identifier_tuple_wise_user_ag_instance_dto = \
            self._get_ag_id_instance_identifier_tuple_wise_user_ag_instance_dtos(
                user_activity_group_instance_dtos)

        user_activity_group_instance_with_associations = \
            self._get_user_activity_group_instance_with_associations(
                activity_group_id_wise_instance_identifier,
                activity_group_id_wise_association_ids,
                activity_group_id_wise_frequency_type,
                ag_id_instance_identifier_tuple_wise_user_ag_instance_dto,
                activity_group_id_association_id_wise_instance_identifiers,
                user_id)

        return user_activity_group_instance_with_associations

    def _get_activity_groups_data(
            self, activity_group_association_dtos:
            List[ActivityGroupAssociationDTO],
    ) -> Tuple[List[ActivityGroupFrequencyConfigDTO],
               List[ActivityGroupInstanceIdentifierDTO]]:
        activity_group_ids = \
            self._filter_activity_group_ids_based_on_association_type(
                activity_group_association_dtos)

        activity_group_frequency_config_dtos = \
            self.activity_group_storage.get_activity_groups_frequency_configs(
                activity_group_ids)

        activity_group_instance_identifier_dtos = \
            self.get_activity_group_instance_identifier(
                activity_group_frequency_config_dtos)

        return activity_group_frequency_config_dtos, \
            activity_group_instance_identifier_dtos

    @staticmethod
    def _get_activity_group_id_wise_frequency_type(
            activity_group_frequency_config_dtos:
            List[ActivityGroupFrequencyConfigDTO]) -> \
            Dict[str, FrequencyTypeEnum]:
        activity_group_wise_frequency_type = {
            dto.activity_group_id: dto.frequency_type
            for dto in activity_group_frequency_config_dtos
        }
        return activity_group_wise_frequency_type

    @staticmethod
    def _filter_activity_group_ids_based_on_association_type(
            activity_group_association_dtos:
            List[ActivityGroupAssociationDTO]) -> List[str]:
        activity_group_ids = []
        for dto in activity_group_association_dtos:
            activity_group_ids.append(dto.activity_group_id)
            if dto.association_type == \
                    ActivityGroupAssociationTypeEnum.ACTIVITY_GROUP.value:
                activity_group_ids.append(dto.association_id)
        return activity_group_ids

    def _get_user_activity_group_instance_with_associations(
            self, activity_group_id_wise_instance_identifier: Dict[str, str],
            activity_group_id_wise_association_ids: Dict[str, List[str]],
            activity_group_wise_frequency_type: Dict[str, FrequencyTypeEnum],
            ag_id_instance_identifier_tuple_wise_user_ag_instance_dto:
            Dict[Tuple[str, str], UserActivityGroupInstanceDTO],
            activity_group_id_association_id_wise_instance_identifiers:
            Dict[Tuple[str, str], List[str]],
            user_id: str,
    ) -> List[UserActivityGroupInstanceWithAssociationDTO]:
        user_activity_group_instance_with_associations = []
        for activity_group_id, association_ids \
                in activity_group_id_wise_association_ids.items():
            instance_identifier = \
                activity_group_id_wise_instance_identifier[activity_group_id]
            user_activity_group_instance_dto = \
                ag_id_instance_identifier_tuple_wise_user_ag_instance_dto.get(
                    (activity_group_id, instance_identifier))

            association_activity_group_instance_dtos = []
            for association_id in association_ids:
                ag_association_instance_identifiers = \
                    activity_group_id_association_id_wise_instance_identifiers[
                        (activity_group_id, association_id)]

                for identifier in ag_association_instance_identifiers:
                    user_activity_group_association_instance_dto = \
                        ag_id_instance_identifier_tuple_wise_user_ag_instance_dto.get(
                            (association_id, identifier))
                    if user_activity_group_association_instance_dto:
                        activity_group_instance_dto = \
                            self._convert_user_ag_instance_dto_to_ag_instance_dto(
                                user_activity_group_association_instance_dto)
                    else:
                        activity_group_instance_dto = \
                            self._prepare_activity_group_instance_dto(
                                association_id, identifier)

                    association_activity_group_instance_dtos.append(
                        activity_group_instance_dto)

            if user_activity_group_instance_dto:
                activity_group_instance_dto = \
                    self._convert_user_ag_instance_dto_to_ag_instance_dto(
                        user_activity_group_instance_dto)
            else:
                activity_group_instance_dto = \
                    self._prepare_activity_group_instance_dto(
                        activity_group_id, instance_identifier)

            user_activity_group_instance_with_associations.append(
                UserActivityGroupInstanceWithAssociationDTO(
                    user_id=user_id,
                    frequency_type=activity_group_wise_frequency_type[
                        activity_group_id],
                    activity_group_instance=activity_group_instance_dto,
                    association_activity_group_instances
                    =association_activity_group_instance_dtos,
                ),
            )

        return user_activity_group_instance_with_associations

    @staticmethod
    def _get_ag_id_instance_identifier_tuple_wise_user_ag_instance_dtos(
            user_activity_group_instance_dtos):
        ag_id_instance_identifier_tuple_wise_user_ag_instance_dto = {}
        for dto in user_activity_group_instance_dtos:
            ag_id_instance_identifier_tuple_wise_user_ag_instance_dto[
                (dto.activity_group_id, dto.instance_identifier)] = dto
        return ag_id_instance_identifier_tuple_wise_user_ag_instance_dto

    def _convert_user_ag_instance_dto_to_ag_instance_dto(
            self, user_ag_instance_dto: UserActivityGroupInstanceDTO,
    ) -> ActivityGroupInstanceDTO:
        start_datetime, end_datetime = \
            self.split_instance_identifier_into_datetime_objects(
                user_ag_instance_dto.instance_identifier)

        activity_group_instance_dto = ActivityGroupInstanceDTO(
            activity_group_id=user_ag_instance_dto.activity_group_id,
            completion_status=user_ag_instance_dto.completion_status,
            completion_percentage=user_ag_instance_dto.completion_percentage,
            instance_identifier=user_ag_instance_dto.instance_identifier,
            instance_type=user_ag_instance_dto.instance_type,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
        return activity_group_instance_dto

    def _prepare_activity_group_instance_dto(
            self, activity_group_id: str, instance_identifier: str,
    ) -> ActivityGroupInstanceDTO:
        start_datetime, end_datetime = \
            self.split_instance_identifier_into_datetime_objects(
                instance_identifier)
        activity_group_instance_dto = ActivityGroupInstanceDTO(
            activity_group_id=activity_group_id,
            completion_status=CompletionStatusEnum.YET_TO_START.value,
            completion_percentage=0.0,
            instance_identifier=instance_identifier,
            instance_type=InstanceTypeEnum.DEFAULT.value,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
        return activity_group_instance_dto

    @staticmethod
    def _get_user_specific_activity_group_instance_identifier_dtos(
            activity_group_id_wise_instance_identifier: Dict[str, str],
            activity_group_id_association_id_wise_instance_identifiers:
            Dict[Tuple[str, str], List[str]],
    ) -> List[ActivityGroupInstanceIdentifierDTO]:
        user_specific_ag_instance_identifier_dtos = []
        for activity_group_id, instance_identifier in \
                activity_group_id_wise_instance_identifier.items():
            user_specific_ag_instance_identifier_dtos.append(
                ActivityGroupInstanceIdentifierDTO(
                    activity_group_id=activity_group_id,
                    instance_identifier=instance_identifier,
                ),
            )

        for activity_group_id_association_id, instance_identifiers in \
                activity_group_id_association_id_wise_instance_identifiers\
                .items():
            for instance_identifier in instance_identifiers:
                user_specific_ag_instance_identifier_dtos.append(
                    ActivityGroupInstanceIdentifierDTO(
                        activity_group_id=activity_group_id_association_id[1],
                        instance_identifier=instance_identifier,
                    ),
                )

        return user_specific_ag_instance_identifier_dtos

    def _get_activity_group_id_association_id_wise_instance_identifiers(
            self, activity_group_id_wise_instance_identifier: Dict[str, str],
            activity_group_id_wise_association_ids: Dict[str, List[str]],
    ) -> Dict[Tuple[str, str], List[str]]:
        activity_group_id_association_id_wise_instance_identifiers = \
            defaultdict(list)
        for activity_group_id, association_ids in \
                activity_group_id_wise_association_ids.items():
            instance_identifier = \
                activity_group_id_wise_instance_identifier[activity_group_id]
            start_datetime, end_datetime = \
                self.split_instance_identifier_into_datetime_objects(
                    instance_identifier)
            start_date = start_datetime.date()
            end_date = end_datetime.date()

            while start_date <= end_date:
                for association_id in association_ids:
                    instance_identifier = \
                        activity_group_id_wise_instance_identifier.get(
                            association_id)

                    if not instance_identifier:
                        continue

                    start_datetime, end_datetime = \
                        self.split_instance_identifier_into_datetime_objects(
                            instance_identifier)
                    start_time = start_datetime.time()
                    end_time = end_datetime.time()

                    start_datetime = datetime.datetime.combine(
                        start_date, start_time)
                    end_datetime = datetime.datetime.combine(
                        start_date, end_time)

                    association_instance_identifier = \
                        self.format_instance_identifier(
                            start_datetime, end_datetime)

                    activity_group_id_association_id_wise_instance_identifiers[
                        (activity_group_id, association_id)
                    ].append(association_instance_identifier)

                start_date += datetime.timedelta(days=1)

        return activity_group_id_association_id_wise_instance_identifiers

    @staticmethod
    def _get_activity_group_id_wise_association_ids(
            activity_group_association_dtos: List[ActivityGroupAssociationDTO],
    ) -> Dict[str, List[str]]:
        activity_group_id_wise_association_ids = defaultdict(list)
        for dto in activity_group_association_dtos:
            activity_group_id_wise_association_ids[
                dto.activity_group_id].append(dto.association_id)
        return activity_group_id_wise_association_ids

    @staticmethod
    def _get_activity_group_id_wise_instance_identifier(
            activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO]) -> Dict[str, str]:
        activity_group_id_wise_instance_identifier = {
            dto.activity_group_id: dto.instance_identifier
            for dto in activity_group_instance_identifier_dtos
        }
        return activity_group_id_wise_instance_identifier

    def get_user_streak_activity_group_instances_for_given_dates(
            self, user_id: str, instance_dates: List[datetime.date],
            instance_types: List[InstanceTypeEnum]) -> \
            List[UserActivityGroupInstanceWithDatetimeDTO]:
        activity_group_ids = \
            self.activity_group_storage.get_streak_enabled_activity_group_ids()

        activity_group_frequency_config_dtos = \
            self.activity_group_storage.get_activity_groups_frequency_configs(
                activity_group_ids)

        activity_group_instance_identifier_dtos = \
            self.get_activity_group_instance_identifier_for_given_dates(
                activity_group_frequency_config_dtos, instance_dates)

        user_activity_group_instance_dtos = \
            self.activity_group_storage \
                .get_user_activity_group_instances_of_given_types(
                    user_id, activity_group_instance_identifier_dtos,
                    instance_types)

        user_activity_group_instance_with_datetime_dtos = \
            self._add_datetime_to_user_agi_dtos(
                user_activity_group_instance_dtos)

        return user_activity_group_instance_with_datetime_dtos

    def get_user_streak_activity_group_instances_between_given_dates(
            self, user_id: str, from_date: datetime.date,
            to_date: datetime.date, instance_types: List[InstanceTypeEnum]) \
            -> List[UserActivityGroupInstanceWithDatetimeDTO]:
        instance_dates = self._prepare_instance_dates(from_date, to_date)

        return self.get_user_streak_activity_group_instances_for_given_dates(
            user_id, instance_dates, instance_types)

    @staticmethod
    def _prepare_instance_dates(
            from_date: datetime.date, to_date: datetime.date) \
            -> List[datetime.date]:
        instance_dates = [
            from_date + datetime.timedelta(days=day_count)
            for day_count in range((to_date - from_date).days + 1)
        ]
        return instance_dates

    def _add_datetime_to_user_agi_dtos(
            self, user_agi_dtos: List[UserActivityGroupInstanceDTO]):
        user_agi_dtos_with_datetimes = []
        for dto in user_agi_dtos:
            start_datetime, end_datetime = \
                self.split_instance_identifier_into_datetime_objects(
                    dto.instance_identifier)
            user_agi_dtos_with_datetimes.append(
                UserActivityGroupInstanceWithDatetimeDTO(
                    id=dto.id,
                    user_id=dto.user_id,
                    activity_group_id=dto.activity_group_id,
                    completion_status=dto.completion_status,
                    completion_percentage=dto.completion_percentage,
                    instance_identifier=dto.instance_identifier,
                    instance_type=dto.instance_type,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                ),
            )
        return user_agi_dtos_with_datetimes

    def get_agi_user_ids_for_date_for_given_completion_types(
            self, activity_group_ids: List[str],
            instance_types: List[InstanceTypeEnum],
            instance_date: datetime.date, user_ids: List[str],
            completion_types: List[CompletionStatusEnum]
    ) -> List[str]:
        activity_group_frequency_config_dtos = \
            self.activity_group_storage.get_activity_groups_frequency_configs(
                activity_group_ids)

        activity_group_instance_identifier_dtos = \
            self.get_activity_group_instance_identifier(
                activity_group_frequency_config_dtos, instance_date)

        user_ids = self.activity_group_storage \
            .get_agi_user_ids_for_instance_types_completion_types(
                activity_group_instance_identifier_dtos, instance_types,
                user_ids, completion_types)

        return user_ids

import datetime
from dataclasses import dataclass
from typing import List, Optional

from nw_activities.constants.enum import TransactionTypeEnum, \
    InstanceTypeEnum, FrequencyTypeEnum, CompletionStatusEnum
from nw_activities.interactors.dtos import UserActivityDTO, \
    UserActivityGroupInstanceWithAssociationDTO, \
    UserActivityGroupCompletionMetricDTO, ActivityGroupIdRewardTypeDTO, \
    UserActivityGroupRewardDetailsDTO, UserInstanceTypeDTO, \
    UserActivityGroupMetricsDTO
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import UserActivityGroupStreakDTO, \
    UserActivityGroupInstanceWithDatetimeDTO


@dataclass
class UserActivityInterfaceDTO:
    user_id: str
    activity_name_enum: str
    entity_id: str
    entity_type: str
    resource_name_enum: str
    resource_value: float
    transaction_type: TransactionTypeEnum


class ServiceInterface:

    @staticmethod
    def create_user_activity(
            user_activity_interface_dto: UserActivityInterfaceDTO):
        user_activity_dto = UserActivityDTO(
            user_id=user_activity_interface_dto.user_id,
            activity_name_enum=user_activity_interface_dto.activity_name_enum,
            entity_id=user_activity_interface_dto.entity_id,
            entity_type=user_activity_interface_dto.entity_type,
            resource_name_enum=user_activity_interface_dto.resource_name_enum,
            resource_value=user_activity_interface_dto.resource_value,
            transaction_type=user_activity_interface_dto.transaction_type,
        )

        from nw_activities.storages.activity_storage_implementation import \
            ActivityStorageImplementation
        from nw_activities.storages.activity_group_storage_implementation \
            import ActivityGroupStorageImplementation
        activity_storage = ActivityStorageImplementation()
        activity_group_storage = ActivityGroupStorageImplementation()

        from nw_activities.interactors.create_user_activity import \
            CreateUserActivityInteractor
        interactor = CreateUserActivityInteractor(
            activity_storage, activity_group_storage)
        interactor.create_user_activity(user_activity_dto)

    @staticmethod
    def get_user_activity_group_instances(user_id: str) -> \
            List[UserActivityGroupInstanceWithAssociationDTO]:
        from nw_activities.interactors.\
            get_user_activity_group_instance_details import \
            GetUserActivityGroupInstanceInteractor
        from nw_activities.storages.\
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetUserActivityGroupInstanceInteractor(
            activity_group_storage)

        response = interactor.get_user_activity_group_instances(user_id)

        return response

    @staticmethod
    def get_user_activity_group_completion_metrics(
            user_id: str, activity_group_ids: List[str],
            instance_date: Optional[datetime.date] = None) -> \
            List[UserActivityGroupCompletionMetricDTO]:
        from nw_activities.interactors. \
            get_activity_group_instance_completion_metrics \
            import GetActivityGroupInstanceCompletionMetricInteractor
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetActivityGroupInstanceCompletionMetricInteractor(
            activity_group_storage)

        user_activity_group_completion_metric_dtos = \
            interactor.get_activity_group_instance_completion_metrics(
                user_id, activity_group_ids, instance_date)

        return user_activity_group_completion_metric_dtos

    @staticmethod
    def get_user_activity_group_reward_details(
            user_id: str, activity_group_reward_type_dtos:
            List[ActivityGroupIdRewardTypeDTO]) -> \
            List[UserActivityGroupRewardDetailsDTO]:
        from nw_activities.interactors.get_user_activity_group_reward_details \
            import GetUserActivityGroupRewardDetailsInteractor
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetUserActivityGroupRewardDetailsInteractor(
            activity_group_storage)

        user_activity_group_reward_details_dtos = \
            interactor.get_user_activity_group_reward_details(
                user_id, activity_group_reward_type_dtos)

        return user_activity_group_reward_details_dtos

    @staticmethod
    def create_user_activity_group_instance_with_daily_frequency(
            user_instance_type_dtos: List[UserInstanceTypeDTO],
            instance_date: datetime.date = None):
        from nw_activities.interactors.create_user_activity_group_instances \
            import CreateUserActivityGroupInstanceInteractor
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = CreateUserActivityGroupInstanceInteractor(
            activity_group_storage)

        interactor.create_user_activity_group_instance_with_daily_frequency(
            user_instance_type_dtos, instance_date)

    @staticmethod
    def get_agi_user_ids_for_instance_and_frequency_type(
            instance_type: InstanceTypeEnum,
            frequency_type: FrequencyTypeEnum) -> List[str]:
        from nw_activities.interactors.\
            get_user_activity_group_instance_details import \
            GetUserActivityGroupInstanceInteractor
        from nw_activities.storages.\
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetUserActivityGroupInstanceInteractor(
            activity_group_storage)

        user_ids = interactor.get_agi_user_ids_for_instance_and_frequency_type(
            instance_type, frequency_type)

        return user_ids

    @staticmethod
    def update_user_activity_group_association_details(
            user_activity_dto: UserActivityDTO):
        from nw_activities.interactors.\
            update_activity_group_association_completion_metrics.activity \
            import ActivityGroupAssociationActivityInteractor
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = ActivityGroupAssociationActivityInteractor(
            activity_group_storage)
        interactor.update_associations_completion_metrics_of_type_activity(
            user_activity_dto)

    @staticmethod
    def get_user_activities(
            user_id: str, from_datetime: datetime.datetime,
            to_datetime: datetime.datetime) -> List[UserActivityDTO]:
        from nw_activities.interactors.interface_interactors.\
            get_user_activities import GetUserActivityInteractor
        from nw_activities.storages.activity_storage_implementation import \
            ActivityStorageImplementation
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_storage = ActivityStorageImplementation()
        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetUserActivityInteractor(
            activity_storage, activity_group_storage)
        return interactor.get_user_activities(
            user_id, from_datetime, to_datetime)

    @staticmethod
    def get_activity_group_instance_metrics_between_dates(
            user_id: str, activity_group_ids: List[str],
            from_date: datetime.date, to_date: datetime.date,
    ) -> List[UserActivityGroupMetricsDTO]:
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation
        from nw_activities.interactors.\
            get_user_activity_group_instance_metrics import \
            GetActivityGroupInstanceMetricInteractor

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetActivityGroupInstanceMetricInteractor(
            activity_group_storage)

        return interactor.get_activity_group_instance_metrics_between_dates(
            user_id, activity_group_ids, from_date, to_date)

    @staticmethod
    def get_streak_enabled_activity_group_ids():
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation
        from nw_activities.interactors.interface_interactors.\
            get_activity_group_details import \
            GetActivityGroupDetailsInteractor

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetActivityGroupDetailsInteractor(activity_group_storage)

        return interactor.get_streak_enabled_activity_group_ids()

    @staticmethod
    def get_user_activity_group_streak_details(user_id: str) -> \
            List[UserActivityGroupStreakDTO]:
        from nw_activities.interactors.interface_interactors. \
            get_user_activities import GetUserActivityInteractor
        from nw_activities.storages.activity_storage_implementation import \
            ActivityStorageImplementation
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_storage = ActivityStorageImplementation()
        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetUserActivityInteractor(
            activity_storage, activity_group_storage)
        return interactor.get_user_activity_group_streak_details(
            user_id)

    @staticmethod
    def create_user_streak_activity(
            user_activity_interface_dto: UserActivityInterfaceDTO):
        user_activity_dto = UserActivityDTO(
            user_id=user_activity_interface_dto.user_id,
            activity_name_enum=user_activity_interface_dto.activity_name_enum,
            entity_id=user_activity_interface_dto.entity_id,
            entity_type=user_activity_interface_dto.entity_type,
            resource_name_enum=user_activity_interface_dto.resource_name_enum,
            resource_value=user_activity_interface_dto.resource_value,
            transaction_type=user_activity_interface_dto.transaction_type,
        )

        from nw_activities.storages.activity_storage_implementation import \
            ActivityStorageImplementation
        from nw_activities.storages.activity_group_storage_implementation \
            import ActivityGroupStorageImplementation
        activity_storage = ActivityStorageImplementation()
        activity_group_storage = ActivityGroupStorageImplementation()

        from nw_activities.interactors.create_user_activity import \
            CreateUserActivityInteractor
        interactor = CreateUserActivityInteractor(
            activity_storage, activity_group_storage)
        interactor.create_user_streak_activity(user_activity_dto)

    @staticmethod
    def create_streak_activity_for_streak_enabled_user(
            user_activity_interface_dto: UserActivityInterfaceDTO):
        user_activity_dto = UserActivityDTO(
            user_id=user_activity_interface_dto.user_id,
            activity_name_enum=user_activity_interface_dto.activity_name_enum,
            entity_id=user_activity_interface_dto.entity_id,
            entity_type=user_activity_interface_dto.entity_type,
            resource_name_enum=user_activity_interface_dto.resource_name_enum,
            resource_value=user_activity_interface_dto.resource_value,
            transaction_type=user_activity_interface_dto.transaction_type,
        )

        from nw_activities.storages.activity_storage_implementation import \
            ActivityStorageImplementation
        from nw_activities.storages.activity_group_storage_implementation \
            import ActivityGroupStorageImplementation
        activity_storage = ActivityStorageImplementation()
        activity_group_storage = ActivityGroupStorageImplementation()

        from nw_activities.interactors.create_user_activity import \
            CreateUserActivityInteractor
        interactor = CreateUserActivityInteractor(
            activity_storage, activity_group_storage)
        interactor.create_streak_activity_for_streak_enabled_user(
            user_activity_dto)

    @staticmethod
    def get_activity_group_instance_user_ids_for_date(
            activity_group_ids: List[str],
            instance_types: List[InstanceTypeEnum],
            instance_date: datetime.date,
            user_ids: List[str],
    ) -> List[str]:
        from nw_activities.interactors. \
            get_user_activity_group_instance_details import \
            GetUserActivityGroupInstanceInteractor
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetUserActivityGroupInstanceInteractor(
            activity_group_storage)

        user_ids = interactor.get_activity_group_instance_user_ids_for_date(
            activity_group_ids, instance_types, instance_date, user_ids)

        return user_ids

    @staticmethod
    def update_user_activity_group_streak(
            user_id: str, activity_group_ids: List[str],
            instance_datetime: datetime = None):
        from nw_activities.interactors.update_user_activity_group_streak \
            import UpdateUserActivityGroupStreakInteractor
        from nw_activities.storages.activity_group_storage_implementation \
            import ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = UpdateUserActivityGroupStreakInteractor(
            activity_group_storage)

        return interactor.update_user_activity_group_streak(
            user_id, activity_group_ids, instance_datetime)

    @staticmethod
    def create_user_activity_group_streak_instance_with_daily_frequency(
            user_instance_type_dtos: List[UserInstanceTypeDTO],
            instance_date: datetime.date = None):
        from nw_activities.interactors.create_user_activity_group_instances \
            import CreateUserActivityGroupInstanceInteractor
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = CreateUserActivityGroupInstanceInteractor(
            activity_group_storage)

        interactor.\
            create_user_activity_group_streak_instance_with_daily_frequency(
                user_instance_type_dtos, instance_date)

    @staticmethod
    def get_user_activity_group_streak_details_with_transaction(user_id: str) \
            -> List[UserActivityGroupStreakDTO]:
        from nw_activities.interactors.interface_interactors. \
            get_user_activities import GetUserActivityInteractor
        from nw_activities.storages.activity_storage_implementation import \
            ActivityStorageImplementation
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_storage = ActivityStorageImplementation()
        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetUserActivityInteractor(
            activity_storage, activity_group_storage)
        return \
            interactor.get_user_activity_group_streak_details_with_transaction(
                user_id)

    @staticmethod
    def get_max_streak_for_user_ids(user_ids: List[str]) -> int:
        from nw_activities.interactors.interface_interactors. \
            get_user_activities import GetUserActivityInteractor
        from nw_activities.storages.activity_storage_implementation import \
            ActivityStorageImplementation
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_storage = ActivityStorageImplementation()
        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetUserActivityInteractor(
            activity_storage, activity_group_storage)

        return interactor.get_max_streak_for_user_ids(user_ids)

    @staticmethod
    def update_user_activity_group_streak_last_updated_at(
            user_id: str, last_updated_at: datetime.datetime):
        from nw_activities.interactors.interface_interactors\
            .update_user_activity_group_streak import \
            UpdateUserActivityGroupStreak
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = UpdateUserActivityGroupStreak(activity_group_storage)

        interactor.update_user_activity_group_streak_last_updated_at(
            user_id, last_updated_at)

    @staticmethod
    def delete_streak_users_activity_group_instances_with_daily_frequency(
            user_ids: List[str], instance_date: datetime.date):
        from nw_activities.interactors.create_user_activity_group_instances \
            import CreateUserActivityGroupInstanceInteractor
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = CreateUserActivityGroupInstanceInteractor(
            activity_group_storage)
        interactor\
            .delete_streak_users_activity_group_instances_with_daily_frequency(
                user_ids, instance_date)

    @staticmethod
    def get_user_activity_group_instances_for_given_dates(
            user_id: str, instance_dates: List[datetime.date],
            instance_types: List[InstanceTypeEnum]) \
            -> List[UserActivityGroupInstanceWithDatetimeDTO]:
        from nw_activities.interactors. \
            get_user_activity_group_instance_details import \
            GetUserActivityGroupInstanceInteractor
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetUserActivityGroupInstanceInteractor(
            activity_group_storage)

        user_activity_group_instance_dtos = \
            interactor.get_user_streak_activity_group_instances_for_given_dates(
                user_id, instance_dates, instance_types)

        return user_activity_group_instance_dtos

    @staticmethod
    def get_user_streak_activity_group_instances_between_given_dates(
            user_id: str, from_date: datetime.date,
            to_date: datetime.date, instance_types: List[InstanceTypeEnum]) \
            -> List[UserActivityGroupInstanceWithDatetimeDTO]:
        from nw_activities.interactors. \
            get_user_activity_group_instance_details import \
            GetUserActivityGroupInstanceInteractor
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetUserActivityGroupInstanceInteractor(
            activity_group_storage)

        user_activity_group_instance_dtos = interactor. \
            get_user_streak_activity_group_instances_between_given_dates(
                user_id, from_date, to_date, instance_types)

        return user_activity_group_instance_dtos

    @staticmethod
    def get_user_activity_group_streaks_up_to_max_rank(
            user_ids: List[str], activity_group_ids: List[str],
            max_rank: int) -> List[UserActivityGroupStreakDTO]:
        from nw_activities.interactors.interface_interactors. \
            get_user_activity_group_streak_details import \
            GetUserActivityGroupStreakDetails
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetUserActivityGroupStreakDetails(activity_group_storage)
        return interactor.get_user_activity_group_streaks_up_to_max_rank(
            user_ids, activity_group_ids, max_rank)

    @staticmethod
    def get_user_activity_group_streak_for_given_streak(
            activity_group_ids: List[str], streak: int) -> List[
        UserActivityGroupStreakDTO]:
        from nw_activities.interactors.interface_interactors. \
            get_user_activity_group_streak_details import \
            GetUserActivityGroupStreakDetails
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetUserActivityGroupStreakDetails(activity_group_storage)
        return interactor.get_user_activity_group_streak_for_given_streak(
            activity_group_ids, streak)

    @staticmethod
    def get_user_activity_group_streaks_for_user_ids(
            user_ids: List[str], activity_group_ids: List[str],
    ) -> List[UserActivityGroupStreakDTO]:
        from nw_activities.interactors.interface_interactors. \
            get_user_activity_group_streak_details import \
            GetUserActivityGroupStreakDetails
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetUserActivityGroupStreakDetails(activity_group_storage)
        return interactor.get_user_activity_group_streaks_for_user_ids(
            user_ids, activity_group_ids)

    @staticmethod
    def get_activity_group_instance_user_ids_for_date_and_completion_status(
            activity_group_ids: List[str],
            instance_types: List[InstanceTypeEnum],
            instance_date: datetime.date,
            user_ids: List[str],
            completion_types: List[CompletionStatusEnum]) -> List[str]:
        from nw_activities.interactors. \
            get_user_activity_group_instance_details import \
            GetUserActivityGroupInstanceInteractor
        from nw_activities.storages. \
            activity_group_storage_implementation import \
            ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = GetUserActivityGroupInstanceInteractor(
            activity_group_storage)

        user_ids = \
            interactor.get_agi_user_ids_for_date_for_given_completion_types(
                activity_group_ids, instance_types, instance_date, user_ids,
                completion_types)

        return user_ids

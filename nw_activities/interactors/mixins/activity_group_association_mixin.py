import datetime
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

from ib_common.date_time_utils.get_current_local_date_time import \
    get_current_local_date_time

from nw_activities.adapters.service_adapter import get_service_adapter
from nw_activities.constants.enum import InstanceTypeEnum, CompletionStatusEnum
from nw_activities.interactors.mixins.common import CommonMixin
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import ActivityGroupStorageInterface, \
    ActivityGroupFrequencyConfigDTO, UserActivityGroupInstanceDTO, \
    ActivityGroupInstanceIdentifierDTO, ActivityGroupCompletionMetricDTO, \
    UserActivityGroupInstanceMetricTrackerDTO, ActivityGroupOptionalMetricDTO


class ActivityGroupAssociationMixin(CommonMixin):

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        self.activity_group_storage = activity_group_storage

    def get_or_create_user_activity_group_instances_for_instance_type(
            self, user_id: str, activity_group_ids: List[str],
            activity_group_frequency_config_dtos:
            List[ActivityGroupFrequencyConfigDTO],
            instance_type: InstanceTypeEnum):

        user_activity_group_instance_dtos = \
            self._get_or_create_user_activity_group_instances(
                activity_group_ids, user_id,
                activity_group_frequency_config_dtos)

        filtered_user_activity_group_instance_dtos = [
            dto
            for dto in user_activity_group_instance_dtos
            if dto.instance_type == instance_type
        ]

        return filtered_user_activity_group_instance_dtos

    def get_or_create_user_activity_group_instances(
            self, user_id: str, activity_group_ids: List[str],
            activity_group_frequency_config_dtos:
            List[ActivityGroupFrequencyConfigDTO],
            instance_datetime: datetime.datetime = None,
    ) -> List[UserActivityGroupInstanceDTO]:
        user_activity_group_instance_dtos = \
            self._get_or_create_user_activity_group_instances(
                activity_group_ids, user_id,
                activity_group_frequency_config_dtos, instance_datetime)
        return user_activity_group_instance_dtos

    def get_activity_group_id_wise_completion_metric_dtos(
            self, activity_group_ids: List[str],
    ) -> Dict[str, List[ActivityGroupCompletionMetricDTO]]:
        activity_group_completion_metric_dtos = \
            self.activity_group_storage.get_activity_groups_completion_metrics(
                activity_group_ids)

        activity_group_id_wise_completion_metric_dtos = defaultdict(list)
        for dto in activity_group_completion_metric_dtos:
            activity_group_id = str(dto.activity_group_id)
            activity_group_id_wise_completion_metric_dtos[
                activity_group_id].append(dto)

        return activity_group_id_wise_completion_metric_dtos

    def get_activity_group_id_wise_optional_metric_dtos(
            self, activity_group_ids: List[str],
    ) -> Dict[str, List[ActivityGroupOptionalMetricDTO]]:
        activity_group_optional_metric_dtos = \
            self.activity_group_storage.get_activity_groups_optional_metrics(
                activity_group_ids)

        activity_group_id_wise_optional_metric_dtos = defaultdict(list)
        for dto in activity_group_optional_metric_dtos:
            activity_group_id = str(dto.activity_group_id)
            activity_group_id_wise_optional_metric_dtos[
                activity_group_id].append(dto)

        return activity_group_id_wise_optional_metric_dtos

    def get_user_activity_group_instances_metric_tracker(
            self, user_activity_group_instance_ids: List[str],
    ) -> List[UserActivityGroupInstanceMetricTrackerDTO]:
        user_ag_instance_metric_tracker_dtos = self.activity_group_storage. \
            get_user_activity_group_instances_metric_tracker(
                user_activity_group_instance_ids)
        return user_ag_instance_metric_tracker_dtos

    def update_user_activity_group_instance_completion_details(
            self, activity_group_id_wise_completion_metric_dtos,
            user_activity_group_instance_metric_tracker_dtos:
            List[UserActivityGroupInstanceMetricTrackerDTO],
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO]) -> List[str]:
        ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto = \
            self.get_ag_completion_metric_id_agi_id_wise_user_agi_metric_tracker_dto(
                user_activity_group_instance_metric_tracker_dtos)

        activity_group_id_wise_user_activity_group_instance_dto = {
            dto.activity_group_id: dto
            for dto in user_activity_group_instance_dtos
        }

        user_activity_group_instances_to_update = []
        completed_activity_group_ids = []
        for activity_group_id, completion_metric_dtos in \
                activity_group_id_wise_completion_metric_dtos.items():
            user_activity_group_instance_dto = \
                activity_group_id_wise_user_activity_group_instance_dto.get(
                    activity_group_id)

            if not user_activity_group_instance_dto:
                continue

            if user_activity_group_instance_dto.completion_percentage == 100:
                continue

            completion_metric_completion_percentages = []
            for dto in completion_metric_dtos:
                agi_metric_id_agi_id_tuple = (
                    dto.id, user_activity_group_instance_dto.id)

                user_agi_metric_tracker_dto = \
                    ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto\
                    .get(agi_metric_id_agi_id_tuple)
                current_value = 0
                if user_agi_metric_tracker_dto:
                    current_value = user_agi_metric_tracker_dto.current_value

                completion_percentage = round(
                    current_value / dto.value, 2) * 100
                completion_percentage = min(completion_percentage, 100)

                completion_metric_completion_percentages.append(
                    completion_percentage)

            completion_status = CompletionStatusEnum.IN_PROGRESS.value
            activity_group_completion_percentage = round(
                sum(completion_metric_completion_percentages) /
                len(completion_metric_completion_percentages), 2,
            )
            if activity_group_completion_percentage >= 100:
                activity_group_completion_percentage = 100
                completion_status = CompletionStatusEnum.COMPLETED.value

            user_activity_group_instance_dto.completion_status = \
                completion_status
            user_activity_group_instance_dto.completion_percentage = \
                activity_group_completion_percentage

            if activity_group_completion_percentage == 100:
                completed_activity_group_ids.append(activity_group_id)

            user_activity_group_instances_to_update.append(
                user_activity_group_instance_dto)

        if user_activity_group_instances_to_update:
            self.activity_group_storage.update_user_activity_group_instances(
                user_activity_group_instances_to_update)

        return completed_activity_group_ids

    @staticmethod
    def get_user_activity_group_instance_ids(
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO]) -> List[str]:
        user_activity_group_instance_ids = [
            dto.id for dto in user_activity_group_instance_dtos
        ]
        return user_activity_group_instance_ids

    @staticmethod
    def get_ag_completion_metric_id_agi_id_wise_user_agi_metric_tracker_dto(
            user_ag_instance_metric_tracker_dtos:
            List[UserActivityGroupInstanceMetricTrackerDTO],
    ) -> Dict[Tuple[str, str], UserActivityGroupInstanceMetricTrackerDTO]:
        ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto = {
            (dto.activity_group_completion_metric_id,
             dto.user_activity_group_instance_id): dto
            for dto in user_ag_instance_metric_tracker_dtos
            if dto.activity_group_completion_metric_id
        }
        return ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto

    @staticmethod
    def get_ag_optional_metric_id_agi_id_wise_user_agi_metric_tracker_dto(
            user_ag_instance_metric_tracker_dtos:
            List[UserActivityGroupInstanceMetricTrackerDTO],
    ) -> Dict[Tuple[str, str], UserActivityGroupInstanceMetricTrackerDTO]:
        ag_optional_id_agi_id_wise_user_agi_metric_tracker_dto = {
            (dto.activity_group_optional_metric_id,
             dto.user_activity_group_instance_id): dto
            for dto in user_ag_instance_metric_tracker_dtos
            if dto.activity_group_optional_metric_id
        }
        return ag_optional_id_agi_id_wise_user_agi_metric_tracker_dto

    @staticmethod
    def get_activity_group_id_wise_user_activity_group_instance_id(
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO]) -> Dict[str, str]:
        activity_group_id_wise_user_activity_group_instance_id = {
            dto.activity_group_id: dto.id
            for dto in user_activity_group_instance_dtos
        }
        return activity_group_id_wise_user_activity_group_instance_id

    def _get_or_create_user_activity_group_instances(
            self, activity_group_ids: List[str], user_id: str,
            activity_group_frequency_config_dtos:
            List[ActivityGroupFrequencyConfigDTO],
            instance_datetime: datetime.datetime = None,
    ) -> List[UserActivityGroupInstanceDTO]:
        instance_date = None
        if instance_datetime:
            instance_date = instance_datetime.date()

        activity_group_instance_identifier_dtos = \
            self.get_activity_group_instance_identifier(
                activity_group_frequency_config_dtos, instance_date)

        required_activity_group_instance_identifier_dtos = \
            self._filter_activity_group_instance_dtos_based_on_frequency_config(
                activity_group_instance_identifier_dtos, instance_datetime)

        if not required_activity_group_instance_identifier_dtos:
            return []

        user_activity_group_instance_dtos = \
            self.activity_group_storage.get_user_activity_group_instances(
                user_id, required_activity_group_instance_identifier_dtos)

        if not user_activity_group_instance_dtos:
            user_activity_group_instance_dtos = \
                self._create_user_activity_group_instances(
                    activity_group_ids, user_id,
                    activity_group_instance_identifier_dtos, instance_date)

        return user_activity_group_instance_dtos

    def _filter_activity_group_instance_dtos_based_on_frequency_config(
            self, activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO],
            instance_datetime: datetime = None) -> \
            List[ActivityGroupInstanceIdentifierDTO]:

        if not instance_datetime:
            instance_datetime = get_current_local_date_time()

        required_activity_group_instance_identifier_dtos = []
        for dto in activity_group_instance_identifier_dtos:
            start_datetime, end_datetime = \
                self.split_instance_identifier_into_datetime_objects(
                    dto.instance_identifier)
            if start_datetime <= instance_datetime <= end_datetime:
                required_activity_group_instance_identifier_dtos.append(dto)

        return required_activity_group_instance_identifier_dtos

    def _create_user_activity_group_instances(
            self, activity_group_ids: List[str], user_id: str,
            activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO],
            instance_date: Optional[datetime.date]
    ) -> List[UserActivityGroupInstanceDTO]:
        activity_group_id_wise_instance_identifier = \
            self._get_activity_group_id_wise_instance_identifier(
                activity_group_instance_identifier_dtos)

        from nw_activities.utils.generate_uuid import generate_uuid

        adapter = get_service_adapter()

        if not instance_date:
            instance_date = get_current_local_date_time().date()

        instance_type = adapter.gamification_wrapper\
            .get_user_activity_group_instance_type(user_id, instance_date)

        if not instance_type:
            instance_type = InstanceTypeEnum.DEFAULT.value

        user_activity_group_instance_dtos = [
            UserActivityGroupInstanceDTO(
                id=generate_uuid(),
                user_id=user_id,
                instance_identifier=
                activity_group_id_wise_instance_identifier[
                    activity_group_id],
                activity_group_id=activity_group_id,
                completion_percentage=0,
                completion_status=CompletionStatusEnum.YET_TO_START.value,
                instance_type=instance_type,
            )
            for activity_group_id in activity_group_ids
        ]

        self.activity_group_storage.create_user_activity_group_instances(
            user_activity_group_instance_dtos)

        return user_activity_group_instance_dtos

    @staticmethod
    def _get_activity_group_id_wise_instance_identifier(
            activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO]) -> Dict[str, str]:
        activity_group_id_wise_instance_identifier = {
            dto.activity_group_id: dto.instance_identifier
            for dto in activity_group_instance_identifier_dtos
        }
        return activity_group_id_wise_instance_identifier

import datetime
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

from nw_activities.constants.enum import CompletionStatusEnum
from nw_activities.interactors.dtos import UserCompletionMetricDTO, \
    UserActivityGroupCompletionMetricDTO
from nw_activities.interactors.mixins.common import CommonMixin
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import ActivityGroupStorageInterface, \
    ActivityGroupCompletionMetricDTO, UserActivityGroupInstanceDTO, \
    UserActivityGroupInstanceMetricTrackerDTO


class GetActivityGroupInstanceCompletionMetricInteractor(CommonMixin):

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        self.activity_group_storage = activity_group_storage

    def get_activity_group_instance_completion_metrics(
            self, user_id: str, activity_group_ids: List[str],
            instance_date: Optional[datetime.date] = None) -> \
            List[UserActivityGroupCompletionMetricDTO]:
        user_activity_group_instance_dtos = \
            self._get_user_activity_group_instance_dtos(
                activity_group_ids, user_id, instance_date)

        user_activity_group_instance_ids = \
            self._get_user_activity_group_instance_ids(
                user_activity_group_instance_dtos)

        activity_group_id_wise_completion_metric_dtos = \
            self._get_activity_group_id_wise_completion_metric_dtos(
                activity_group_ids)

        user_ag_instance_metric_tracker_dtos = self.activity_group_storage. \
            get_user_activity_group_instances_metric_tracker_without_transaction(
                user_activity_group_instance_ids)

        activity_group_id_wise_user_activity_group_instance_id = \
            self._get_activity_group_id_wise_user_activity_group_instance_id(
                user_activity_group_instance_dtos)

        user_ag_instance_completion_metric_id_wise_metric_tracker_dto = \
            self._get_user_ag_instance_completion_metric_id_wise_metric_tracker_dto(
                user_ag_instance_metric_tracker_dtos)

        activity_group_id_wise_instance_completion_metric_dtos = \
            self._get_activity_group_id_wise_instance_completion_metric_dtos(
                activity_group_id_wise_completion_metric_dtos,
                activity_group_id_wise_user_activity_group_instance_id,
                user_ag_instance_completion_metric_id_wise_metric_tracker_dto)

        activity_group_wise_no_of_activity_group_instances_completed = \
            self._get_activity_group_wise_no_of_activity_group_instances_completed(
                activity_group_ids, user_id)

        user_activity_group_completion_metric_dtos = \
            self._get_user_activity_group_completion_metric_dtos(
                activity_group_id_wise_instance_completion_metric_dtos,
                activity_group_wise_no_of_activity_group_instances_completed)

        return user_activity_group_completion_metric_dtos

    @staticmethod
    def _get_user_activity_group_instance_ids(
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO]) -> List[str]:
        user_activity_group_instance_ids = [
            dto.id for dto in user_activity_group_instance_dtos
        ]
        return user_activity_group_instance_ids

    def _get_user_activity_group_instance_dtos(
            self, activity_group_ids: List[str], user_id: str,
            instance_date: Optional[datetime.date] = None) -> \
            List[UserActivityGroupInstanceDTO]:
        activity_group_frequency_config_dtos = \
            self.activity_group_storage.get_activity_groups_frequency_configs(
                activity_group_ids)

        activity_group_instance_identifier_dtos = \
            self.get_activity_group_instance_identifier(
                activity_group_frequency_config_dtos, instance_date)

        user_activity_group_instance_dtos = \
            self.activity_group_storage.get_user_activity_group_instances(
                user_id, activity_group_instance_identifier_dtos)

        return user_activity_group_instance_dtos

    @staticmethod
    def _get_user_ag_instance_completion_metric_id_wise_metric_tracker_dto(
            user_ag_instance_metric_tracker_dtos:
            List[UserActivityGroupInstanceMetricTrackerDTO],
    ) -> Dict[Tuple[str, str], UserActivityGroupInstanceMetricTrackerDTO]:
        user_ag_instance_completion_metric_id_wise_metric_tracker_dto = {
            (dto.user_activity_group_instance_id,
             dto.activity_group_completion_metric_id): dto
            for dto in user_ag_instance_metric_tracker_dtos
        }
        return user_ag_instance_completion_metric_id_wise_metric_tracker_dto

    @staticmethod
    def _get_activity_group_id_wise_user_activity_group_instance_id(
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO]) -> Dict[str, str]:
        activity_group_id_wise_user_activity_group_instance_id = {
            dto.activity_group_id: dto.id
            for dto in user_activity_group_instance_dtos
        }
        return activity_group_id_wise_user_activity_group_instance_id

    def _get_activity_group_wise_no_of_activity_group_instances_completed(
            self, activity_group_ids: List[str], user_id: str) -> \
            Dict[str, float]:
        activity_group_instance_completed_count_dtos = \
            self.activity_group_storage \
                .get_activity_group_instances_count_for_completion_status(
                    user_id, activity_group_ids,
                    CompletionStatusEnum.COMPLETED.value)

        activity_group_wise_no_of_activity_group_instances_completed = {
            dto.activity_group_id: dto.activity_group_instances_count
            for dto in activity_group_instance_completed_count_dtos
        }

        return activity_group_wise_no_of_activity_group_instances_completed

    @staticmethod
    def _get_user_activity_group_completion_metric_dtos(
            activity_group_id_wise_instance_completion_metric_dtos:
            Dict[str, List[UserCompletionMetricDTO]],
            activity_group_wise_no_of_activity_group_instances_completed:
            Dict[str, float]) -> List[UserActivityGroupCompletionMetricDTO]:
        user_activity_group_completion_metric_dtos = []
        for activity_group_id, completion_metric_dtos in \
                activity_group_id_wise_instance_completion_metric_dtos.items():
            no_of_instances_completed = \
                activity_group_wise_no_of_activity_group_instances_completed \
                .get(activity_group_id, 0)
            user_activity_group_completion_metric_dtos.append(
                UserActivityGroupCompletionMetricDTO(
                    activity_group_id=activity_group_id,
                    instance_completion_metrics=completion_metric_dtos,
                    no_of_activity_group_instances_completed
                    =no_of_instances_completed,
                ),
            )
        return user_activity_group_completion_metric_dtos

    @staticmethod
    def _get_activity_group_id_wise_instance_completion_metric_dtos(
            activity_group_id_wise_completion_metric_dtos,
            activity_group_id_wise_user_activity_group_instance_id,
            user_ag_instance_completion_metric_id_wise_metric_tracker_dto):
        activity_group_id_wise_instance_completion_metric_dtos = {}
        for activity_group_id, completion_metric_dtos in \
                activity_group_id_wise_completion_metric_dtos.items():
            user_activity_group_instance_id = \
                activity_group_id_wise_user_activity_group_instance_id.get(
                    activity_group_id)
            instance_completion_metric_dtos = []
            for dto in completion_metric_dtos:
                user_ag_completion_metric_tracker_dto = \
                    user_ag_instance_completion_metric_id_wise_metric_tracker_dto.get(
                        (user_activity_group_instance_id, dto.id))
                user_current_value = 0
                if user_ag_completion_metric_tracker_dto:
                    user_current_value = \
                        user_ag_completion_metric_tracker_dto.current_value
                instance_completion_metric_dtos.append(
                    UserCompletionMetricDTO(
                        target_value=dto.value,
                        current_value=user_current_value,
                        entity_id=dto.entity_id,
                        entity_type=dto.entity_type,
                    ),
                )

            activity_group_id_wise_instance_completion_metric_dtos[
                activity_group_id] = instance_completion_metric_dtos

        return activity_group_id_wise_instance_completion_metric_dtos

    def _get_activity_group_id_wise_completion_metric_dtos(
            self, activity_group_ids: List[str]) -> \
            Dict[str, List[ActivityGroupCompletionMetricDTO]]:
        activity_group_completion_metric_dtos = \
            self.activity_group_storage.get_activity_groups_completion_metrics(
                activity_group_ids)

        activity_group_id_wise_completion_metric_dtos = defaultdict(list)
        for dto in activity_group_completion_metric_dtos:
            activity_group_id = str(dto.activity_group_id)
            activity_group_id_wise_completion_metric_dtos[
                activity_group_id].append(dto)

        return activity_group_id_wise_completion_metric_dtos

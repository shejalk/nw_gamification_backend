import datetime
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

from nw_activities.interactors.dtos import UserCompletionMetricDTO, \
    UserOptionalMetricDTO, UserActivityGroupMetricsDTO
from nw_activities.interactors.mixins.common import CommonMixin
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import ActivityGroupStorageInterface, \
    ActivityGroupCompletionMetricDTO, UserActivityGroupInstanceDTO, \
    UserActivityGroupInstanceMetricTrackerDTO, ActivityGroupOptionalMetricDTO


class GetActivityGroupInstanceMetricInteractor(CommonMixin):

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        self.activity_group_storage = activity_group_storage

    def get_activity_group_instance_metrics_between_dates(
            self, user_id: str, activity_group_ids: List[str],
            from_date: datetime.date, to_date: datetime.date,
    ) -> List[UserActivityGroupMetricsDTO]:
        user_activity_group_instance_dtos = \
            self._get_user_activity_group_instance_dtos(
                activity_group_ids, user_id, from_date, to_date)
        return self.get_activity_group_instance_metrics(
            activity_group_ids, user_activity_group_instance_dtos)

    def get_users_activity_group_instance_metrics_for_date(
            self, user_ids: List[str], activity_group_ids: List[str],
            instance_date: datetime.date,
    ) -> List[UserActivityGroupMetricsDTO]:
        activity_group_frequency_config_dtos = \
            self.activity_group_storage.get_activity_groups_frequency_configs(
                activity_group_ids)
        activity_group_instance_identifier_dtos = \
            self.get_activity_group_instance_identifiers_for_date(
                activity_group_frequency_config_dtos, instance_date)
        user_activity_group_instance_dtos = \
            self.activity_group_storage.get_users_activity_group_instances(
                user_ids, activity_group_instance_identifier_dtos)

        return self.get_activity_group_instance_metrics(
            activity_group_ids, user_activity_group_instance_dtos)

    def get_activity_group_instance_metrics(
            self, activity_group_ids: List[str],
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO],
    ) -> List[UserActivityGroupMetricsDTO]:
        user_activity_group_instance_ids = \
            self._get_user_activity_group_instance_ids(
                user_activity_group_instance_dtos)

        activity_group_id_wise_completion_metric_dtos = \
            self._get_activity_group_id_wise_completion_metric_dtos(
                activity_group_ids)
        activity_group_id_wise_optional_metric_dtos = \
            self._get_activity_group_id_wise_optional_metric_dtos(
                activity_group_ids)

        user_ag_instance_metric_tracker_dtos = self.activity_group_storage. \
            get_user_activity_group_instances_metric_tracker_without_transaction(
                user_activity_group_instance_ids)

        activity_group_id_wise_user_activity_group_instance_ids = \
            self._get_activity_group_id_wise_user_activity_group_instance_ids(
                user_activity_group_instance_dtos)

        user_ag_instance_completion_metric_id_wise_metric_tracker_dto = \
            self._get_user_ag_instance_completion_metric_id_wise_metric_tracker_dto(
                user_ag_instance_metric_tracker_dtos)
        user_ag_instance_optional_metric_id_wise_metric_tracker_dto = \
            self._get_user_ag_instance_optional_metric_id_wise_metric_tracker_dto(
                user_ag_instance_metric_tracker_dtos)

        user_ag_instance_id_wise_completion_metric_dtos = \
            self._get_user_ag_instance_wise_instance_completion_metrics(
                activity_group_id_wise_completion_metric_dtos,
                activity_group_id_wise_user_activity_group_instance_ids,
                user_ag_instance_completion_metric_id_wise_metric_tracker_dto)
        user_ag_instance_id_wise_optional_metric_dtos = \
            self._get_user_ag_instance_wise_instance_optional_metric_dtos(
                activity_group_id_wise_optional_metric_dtos,
                activity_group_id_wise_user_activity_group_instance_ids,
                user_ag_instance_optional_metric_id_wise_metric_tracker_dto)

        user_activity_group_metric_dtos = \
            self._get_user_activity_group_completion_metric_dtos(
                user_activity_group_instance_dtos,
                user_ag_instance_id_wise_completion_metric_dtos,
                user_ag_instance_id_wise_optional_metric_dtos)

        return user_activity_group_metric_dtos

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
            from_date: datetime.date, to_date: datetime.date) -> \
            List[UserActivityGroupInstanceDTO]:
        activity_group_frequency_config_dtos = \
            self.activity_group_storage.get_activity_groups_frequency_configs(
                activity_group_ids)

        activity_group_instance_identifier_dtos = \
            self.get_activity_group_instance_identifiers_between_dates(
                activity_group_frequency_config_dtos, from_date, to_date)

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
            if dto.activity_group_completion_metric_id
        }
        return user_ag_instance_completion_metric_id_wise_metric_tracker_dto

    @staticmethod
    def _get_user_ag_instance_optional_metric_id_wise_metric_tracker_dto(
            user_ag_instance_metric_tracker_dtos:
            List[UserActivityGroupInstanceMetricTrackerDTO],
    ) -> Dict[Tuple[str, str], UserActivityGroupInstanceMetricTrackerDTO]:
        user_ag_instance_optional_metric_id_wise_metric_tracker_dto = {
            (dto.user_activity_group_instance_id,
             dto.activity_group_optional_metric_id): dto
            for dto in user_ag_instance_metric_tracker_dtos
            if dto.activity_group_optional_metric_id
        }
        return user_ag_instance_optional_metric_id_wise_metric_tracker_dto

    @staticmethod
    def _get_activity_group_id_wise_user_activity_group_instance_ids(
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO]) -> Dict[str, List[str]]:
        activity_group_id_wise_user_activity_group_instance_ids = \
            defaultdict(list)
        for dto in user_activity_group_instance_dtos:
            activity_group_id_wise_user_activity_group_instance_ids[
                dto.activity_group_id].append(dto.id)
        return activity_group_id_wise_user_activity_group_instance_ids

    def _get_user_activity_group_completion_metric_dtos(
            self, user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO],
            user_ag_instance_id_wise_completion_metric_dtos:
            Dict[str, List[UserCompletionMetricDTO]],
            user_ag_instance_id_wise_optional_metric_dtos:
            Dict[str, List[UserOptionalMetricDTO]],
    ) -> List[UserActivityGroupMetricsDTO]:
        user_activity_group_metrics_dtos = []
        for dto in user_activity_group_instance_dtos:
            optional_metric_dtos = \
                user_ag_instance_id_wise_optional_metric_dtos[dto.id]
            completion_metric_dtos = \
                user_ag_instance_id_wise_completion_metric_dtos[dto.id]
            start_datetime, end_datetime = \
                self.split_instance_identifier_into_datetime_objects(
                    dto.instance_identifier)
            user_activity_group_metrics_dto = UserActivityGroupMetricsDTO(
                user_id=dto.user_id,
                instance_id=dto.id,
                instance_identifier=dto.instance_identifier,
                instance_type=dto.instance_type,
                activity_group_id=dto.activity_group_id,
                completion_percentage=dto.completion_percentage,
                completion_status=dto.completion_status,
                instance_completion_metrics=completion_metric_dtos,
                instance_optional_metrics=optional_metric_dtos,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
            )
            user_activity_group_metrics_dtos.append(
                user_activity_group_metrics_dto)

        return user_activity_group_metrics_dtos

    def _get_user_ag_instance_wise_instance_completion_metrics(
            self, activity_group_id_wise_completion_metric_dtos:
            Dict[str, List[ActivityGroupCompletionMetricDTO]],
            activity_group_id_wise_user_activity_group_instance_ids:
            Dict[str, List[str]],
            user_agi_with_completion_metric_id_wise_metric_tracker_dto:
            Dict[Tuple[str, str], UserActivityGroupInstanceMetricTrackerDTO],
    ) -> Dict[str, List[UserCompletionMetricDTO]]:
        user_ag_instance_id_wise_completion_metric_dtos = defaultdict(list)
        for activity_group_id, completion_metric_dtos in \
                activity_group_id_wise_completion_metric_dtos.items():
            user_activity_group_instance_ids = \
                activity_group_id_wise_user_activity_group_instance_ids.get(
                    activity_group_id, [])
            for dto in completion_metric_dtos:
                for instance_id in user_activity_group_instance_ids:
                    user_ag_completion_metric_tracker_dto = \
                        self._get_user_activity_group_completion_metric_tracker(
                            dto.id, instance_id,
                            user_agi_with_completion_metric_id_wise_metric_tracker_dto)
                    user_current_value = 0
                    if user_ag_completion_metric_tracker_dto:
                        user_current_value = \
                            user_ag_completion_metric_tracker_dto.current_value

                    user_ag_instance_id_wise_completion_metric_dtos[
                        instance_id].append(
                            UserCompletionMetricDTO(
                                target_value=dto.value,
                                current_value=user_current_value,
                                entity_id=dto.entity_id,
                                entity_type=dto.entity_type,
                            ),
                        )

        return user_ag_instance_id_wise_completion_metric_dtos

    @staticmethod
    def _get_user_activity_group_completion_metric_tracker(
            completion_metric_id: str,
            activity_group_instance_id: str,
            user_ag_instance_completion_metric_id_wise_metric_tracker_dto:
            Dict[Tuple[str, str], UserActivityGroupInstanceMetricTrackerDTO],
    ) -> Optional[UserActivityGroupInstanceMetricTrackerDTO]:
        user_ag_completion_metric_tracker_dto = \
            user_ag_instance_completion_metric_id_wise_metric_tracker_dto.get(
                (activity_group_instance_id, completion_metric_id))
        return user_ag_completion_metric_tracker_dto

    def _get_user_ag_instance_wise_instance_optional_metric_dtos(
            self, activity_group_id_wise_optional_metric_dtos:
            Dict[str, List[ActivityGroupOptionalMetricDTO]],
            activity_group_id_wise_user_activity_group_instance_ids:
            Dict[str, List[str]],
            user_agi_with_optional_metric_id_wise_metric_tracker_dto:
            Dict[Tuple[str, str], UserActivityGroupInstanceMetricTrackerDTO],
    ):
        user_ag_instance_id_wise_optional_metric_dtos = defaultdict(list)
        for activity_group_id, optional_metric_dtos in \
                activity_group_id_wise_optional_metric_dtos.items():
            user_activity_group_instance_ids = \
                activity_group_id_wise_user_activity_group_instance_ids.get(
                    activity_group_id, [])
            for dto in optional_metric_dtos:
                for instance_id in user_activity_group_instance_ids:
                    user_ag_optional_metric_tracker_dto = \
                        self._get_user_activity_group_optional_metric_tracker(
                            dto.id, instance_id,
                            user_agi_with_optional_metric_id_wise_metric_tracker_dto)
                    user_current_value = 0
                    if user_ag_optional_metric_tracker_dto:
                        user_current_value = \
                            user_ag_optional_metric_tracker_dto.current_value
                    user_ag_instance_id_wise_optional_metric_dtos[
                        instance_id].append(
                            UserOptionalMetricDTO(
                                current_value=user_current_value,
                                entity_id=dto.entity_id,
                                entity_type=dto.entity_type,
                            ),
                        )

        return user_ag_instance_id_wise_optional_metric_dtos

    @staticmethod
    def _get_user_activity_group_optional_metric_tracker(
            optional_metric_id: str,
            activity_group_instance_id: str,
            user_ag_instance_optional_metric_id_wise_metric_tracker_dto:
            Dict[Tuple[str, str], UserActivityGroupInstanceMetricTrackerDTO],
    ) -> Optional[UserActivityGroupInstanceMetricTrackerDTO]:
        user_ag_optional_metric_tracker_dto = \
            user_ag_instance_optional_metric_id_wise_metric_tracker_dto.get(
                (activity_group_instance_id, optional_metric_id))
        return user_ag_optional_metric_tracker_dto

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

    def _get_activity_group_id_wise_optional_metric_dtos(
            self, activity_group_ids: List[str]) -> \
            Dict[str, List[ActivityGroupOptionalMetricDTO]]:
        activity_group_optional_metric_dtos = \
            self.activity_group_storage.get_activity_groups_optional_metrics(
                activity_group_ids)

        activity_group_id_wise_optional_metric_dtos = defaultdict(list)
        for dto in activity_group_optional_metric_dtos:
            activity_group_id = str(dto.activity_group_id)
            activity_group_id_wise_optional_metric_dtos[
                activity_group_id].append(dto)

        return activity_group_id_wise_optional_metric_dtos

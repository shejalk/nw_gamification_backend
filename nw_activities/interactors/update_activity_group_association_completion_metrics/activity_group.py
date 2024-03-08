from collections import defaultdict
from typing import List, Dict, Tuple

from ib_common.decorators.atomic_transaction import atomic_transaction

from nw_activities.adapters.service_adapter import get_service_adapter
from nw_activities.constants.enum import \
    CompletionMetricEntityTypeEnum, InstanceTypeEnum
from nw_activities.interactors.dtos import \
    UserActivityGroupInstanceWithAssociationDTO
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import ActivityGroupStorageInterface, \
    UserActivityGroupInstanceMetricTrackerDTO, \
    ActivityGroupCompletionMetricDTO, ActivityGroupAssociationDTO, \
    ActivityGroupFrequencyConfigDTO, UserActivityGroupInstanceDTO
from nw_activities.interactors.mixins.activity_group_association_mixin import \
    ActivityGroupAssociationMixin


class ActivityGroupAssociationActivityGroupInteractor(
        ActivityGroupAssociationMixin):

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        super().__init__(activity_group_storage)
        self.activity_group_storage = activity_group_storage

    def update_associations_completion_metrics_of_type_activity_group(
            self, user_id: str, activity_group_ids: List[str]):
        activity_group_frequency_config_dtos = \
            self.activity_group_storage.get_activity_groups_frequency_configs(
                activity_group_ids)

        user_activity_group_instance_dtos = \
            self.get_or_create_user_activity_group_instances_for_instance_type(
                user_id, activity_group_ids,
                activity_group_frequency_config_dtos,
                InstanceTypeEnum.DEFAULT.value)

        if not user_activity_group_instance_dtos:
            return

        activity_group_association_dtos = self.activity_group_storage\
            .get_activity_group_associations_for_activity_group_ids(
                activity_group_ids)

        activity_group_id_wise_completion_metric_dtos = \
            self.get_activity_group_id_wise_completion_metric_dtos(
                activity_group_ids)

        updated_user_activity_group_instance_metric_tracker_dtos = \
            self.update_activity_groups_completion_metrics(
                activity_group_association_dtos,
                activity_group_id_wise_completion_metric_dtos,
                user_activity_group_instance_dtos, user_id)

        completed_activity_group_ids = \
            self.update_user_activity_group_instance_completion_details(
                activity_group_id_wise_completion_metric_dtos,
                updated_user_activity_group_instance_metric_tracker_dtos,
                user_activity_group_instance_dtos)

        self._send_activity_group_completed_event(
            user_id, completed_activity_group_ids,
            activity_group_frequency_config_dtos)

        activity_group_association_dtos = self.activity_group_storage.\
            get_activity_group_associations_for_association_ids(
                activity_group_ids)

        if activity_group_association_dtos:
            self.update_associations_completion_metrics_of_type_activity_group(
                user_id, activity_group_ids)

    @atomic_transaction()
    def update_activity_groups_completion_metrics(
            self, activity_group_association_dtos:
            List[ActivityGroupAssociationDTO],
            activity_group_id_wise_completion_metric_dtos:
            Dict[str, List[ActivityGroupCompletionMetricDTO]],
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO],
            user_id: str,
    ) -> List[UserActivityGroupInstanceMetricTrackerDTO]:
        user_activity_group_instance_ids = \
            self.get_user_activity_group_instance_ids(
                user_activity_group_instance_dtos)

        user_ag_instance_metric_tracker_dtos = \
            self.get_user_activity_group_instances_metric_tracker(
                user_activity_group_instance_ids)

        ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto = \
            self.get_ag_completion_metric_id_agi_id_wise_user_agi_metric_tracker_dto(
                user_ag_instance_metric_tracker_dtos)

        activity_group_id_wise_user_activity_group_instance_id = \
            self.get_activity_group_id_wise_user_activity_group_instance_id(
                user_activity_group_instance_dtos)

        user_activity_group_instance_with_associations_dtos = \
            self._get_user_activity_group_instance_with_associations_dtos(
                user_id, activity_group_association_dtos)

        updated_user_activity_group_instance_metric_tracker_dtos = \
            self._update_user_agi_associations_completion_metrics(
                activity_group_id_wise_completion_metric_dtos,
                ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto,
                activity_group_id_wise_user_activity_group_instance_id,
                user_activity_group_instance_with_associations_dtos)

        return updated_user_activity_group_instance_metric_tracker_dtos

    def _update_user_agi_associations_completion_metrics(
            self, activity_group_id_wise_completion_metric_dtos:
            Dict[str, List[ActivityGroupCompletionMetricDTO]],
            ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto:
            Dict[Tuple[str, str], UserActivityGroupInstanceMetricTrackerDTO],
            ag_id_wise_user_activity_group_instance_id: Dict[str, str],
            user_activity_group_instance_with_associations_dtos:
            List[UserActivityGroupInstanceWithAssociationDTO],
    ) -> List[UserActivityGroupInstanceMetricTrackerDTO]:
        activity_group_id_wise_association_id_wise_current_value = {}
        completion_percentage = 100
        for dto in user_activity_group_instance_with_associations_dtos:
            if dto.activity_group_instance.completion_percentage == \
                    completion_percentage:
                continue

            association_id_wise_current_value = defaultdict(float)
            for association_agi_dto in \
                    dto.association_activity_group_instances:
                if association_agi_dto.completion_percentage == \
                        completion_percentage:
                    association_id_wise_current_value[
                        association_agi_dto.activity_group_id] += 1

            activity_group_id_wise_association_id_wise_current_value[
                dto.activity_group_instance.activity_group_id] = \
                association_id_wise_current_value

        updated_user_activity_group_instance_metric_tracker_dtos = \
            self\
            ._create_or_update_user_activity_group_instances_metric_tracker(
                activity_group_id_wise_completion_metric_dtos,
                ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto,
                ag_id_wise_user_activity_group_instance_id,
                activity_group_id_wise_association_id_wise_current_value)

        return updated_user_activity_group_instance_metric_tracker_dtos

    def _get_user_activity_group_instance_with_associations_dtos(
            self, user_id: str,
            activity_group_association_dtos: List[ActivityGroupAssociationDTO],
    ) -> List[UserActivityGroupInstanceWithAssociationDTO]:
        from nw_activities.interactors\
            .get_user_activity_group_instance_details import \
            GetUserActivityGroupInstanceInteractor
        interactor = GetUserActivityGroupInstanceInteractor(
            self.activity_group_storage)
        user_activity_group_instance_with_associations_dtos = \
            interactor\
            .get_user_activity_group_instances_with_associations_instances(
                user_id, activity_group_association_dtos)
        return user_activity_group_instance_with_associations_dtos

    def _create_or_update_user_activity_group_instances_metric_tracker(
            self, activity_group_id_wise_completion_metric_dtos:
            Dict[str, List[ActivityGroupCompletionMetricDTO]],
            ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto:
            Dict[Tuple[str, str], UserActivityGroupInstanceMetricTrackerDTO],
            ag_id_wise_user_activity_group_instance_id: Dict[str, str],
            activity_group_id_wise_association_id_wise_current_value:
            Dict[str, Dict[str, float]],
    ) -> List[UserActivityGroupInstanceMetricTrackerDTO]:
        completion_metric_entity_id_wise_activity_group_id = \
            self._get_completion_metric_entity_id_wise_activity_group_id(
                activity_group_id_wise_completion_metric_dtos)

        user_activity_group_instance_metric_dtos_to_update = []
        user_activity_group_instance_metric_dtos_to_create = []
        for activity_group_id, completion_metric_dtos in \
                activity_group_id_wise_completion_metric_dtos.items():
            association_id_wise_current_value = \
                activity_group_id_wise_association_id_wise_current_value.get(
                    activity_group_id)

            if association_id_wise_current_value is None:
                continue

            user_activity_completion_metric_dtos = \
                self._get_updated_user_activity_completion_metric_dtos(
                    activity_group_id,
                    ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto,
                    ag_id_wise_user_activity_group_instance_id,
                    completion_metric_dtos,
                    completion_metric_entity_id_wise_activity_group_id,
                    association_id_wise_current_value)

            if user_activity_completion_metric_dtos[0]:
                user_activity_group_instance_metric_dtos_to_create.extend(
                    user_activity_completion_metric_dtos[0],
                )

            if user_activity_completion_metric_dtos[1]:
                user_activity_group_instance_metric_dtos_to_update.extend(
                    user_activity_completion_metric_dtos[1],
                )

        if user_activity_group_instance_metric_dtos_to_create:
            self.activity_group_storage \
                .create_user_activity_group_instances_metric_tracker(
                    user_activity_group_instance_metric_dtos_to_create)

        if user_activity_group_instance_metric_dtos_to_update:
            self.activity_group_storage \
                .update_user_activity_group_instances_metric_tracker(
                    user_activity_group_instance_metric_dtos_to_update)

        updated_user_activity_group_instance_metric_dtos = \
            user_activity_group_instance_metric_dtos_to_create + \
            user_activity_group_instance_metric_dtos_to_update

        return updated_user_activity_group_instance_metric_dtos

    def _get_completion_metric_entity_id_wise_activity_group_id(
            self, activity_group_id_wise_completion_metric_dtos:
            Dict[str, List[ActivityGroupCompletionMetricDTO]],
    ) -> Dict[str, str]:
        completion_metric_entity_ids_of_type_ag_association = []
        for _, completion_metric_dtos \
                in activity_group_id_wise_completion_metric_dtos.items():
            for dto in completion_metric_dtos:
                if dto.entity_type == \
                        CompletionMetricEntityTypeEnum\
                        .ACTIVITY_GROUP_ASSOCIATION.value:
                    completion_metric_entity_ids_of_type_ag_association.append(
                        dto.entity_id)

        activity_group_association_dtos = \
            self.activity_group_storage.get_activity_group_associations(
                completion_metric_entity_ids_of_type_ag_association)

        completion_metric_entity_id_wise_activity_group_id = {
            dto.id: dto.activity_group_id
            for dto in activity_group_association_dtos
        }

        return completion_metric_entity_id_wise_activity_group_id

    @staticmethod
    def _get_updated_user_activity_completion_metric_dtos(
            activity_group_id: str,
            ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto:
            Dict[Tuple[str, str], UserActivityGroupInstanceMetricTrackerDTO],
            ag_id_wise_user_activity_group_instance_id: Dict[str, str],
            completion_metric_dtos: List[ActivityGroupCompletionMetricDTO],
            completion_metric_entity_id_wise_activity_group_id: Dict[str, str],
            association_id_wise_current_value: Dict[str, float],
    ) -> Tuple[List[UserActivityGroupInstanceMetricTrackerDTO],
               List[UserActivityGroupInstanceMetricTrackerDTO]]:
        from nw_activities.utils.generate_uuid import generate_uuid

        user_activity_group_instance_metric_dtos_to_create = []
        user_activity_group_instance_metric_dtos_to_update = []
        for dto in completion_metric_dtos:
            if dto.entity_type == \
                    CompletionMetricEntityTypeEnum\
                    .ACTIVITY_GROUP_ASSOCIATION.value:
                association_id = \
                    completion_metric_entity_id_wise_activity_group_id[
                        dto.entity_id]

                current_value = association_id_wise_current_value[
                    association_id]

                user_activity_group_instance_id = \
                    ag_id_wise_user_activity_group_instance_id[
                        activity_group_id]
                ag_completion_metric_id_agi_id_tuple = (
                    dto.id, user_activity_group_instance_id)
                user_agi_metric_tracker_dto = \
                    ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto\
                    .get(ag_completion_metric_id_agi_id_tuple)

                if user_agi_metric_tracker_dto:
                    if user_agi_metric_tracker_dto.current_value != \
                            current_value:
                        user_agi_metric_tracker_dto.current_value = \
                            current_value
                        user_activity_group_instance_metric_dtos_to_update\
                            .append(user_agi_metric_tracker_dto)
                else:
                    user_agi_metric_tracker_dto = \
                        UserActivityGroupInstanceMetricTrackerDTO(
                            id=generate_uuid(),
                            user_activity_group_instance_id=
                            user_activity_group_instance_id,
                            activity_group_completion_metric_id=dto.id,
                            current_value=current_value,
                            activity_group_optional_metric_id=None,
                        )
                    user_activity_group_instance_metric_dtos_to_create.append(
                        user_agi_metric_tracker_dto)

        return user_activity_group_instance_metric_dtos_to_create, \
            user_activity_group_instance_metric_dtos_to_update

    def _send_activity_group_completed_event(
            self, user_id: str, activity_group_ids: List[str],
            frequency_config_dtos: List[ActivityGroupFrequencyConfigDTO]):

        if not activity_group_ids:
            return

        streak_enabled_activity_group_ids = \
            self.activity_group_storage.get_streak_enabled_activity_group_ids()

        activity_group_ids = list(set(activity_group_ids) -
                                  set(streak_enabled_activity_group_ids))

        if not activity_group_ids:
            return

        activity_group_id_wise_frequency_config_dto = {
            dto.activity_group_id: dto
            for dto in frequency_config_dtos
        }

        adapter = get_service_adapter()
        for activity_group_id in activity_group_ids:
            frequency_config_dto = \
                activity_group_id_wise_frequency_config_dto[activity_group_id]
            adapter.ws_service.send_activity_group_completed_event(
                user_id, activity_group_id,
                frequency_config_dto.frequency_type)

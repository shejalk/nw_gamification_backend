from typing import List, Dict, Tuple

from ib_common.decorators.atomic_transaction import atomic_transaction

from nw_activities.adapters.service_adapter import get_service_adapter
from nw_activities.constants.enum import \
    InstanceTypeEnum
from nw_activities.interactors.dtos import UserActivityDTO
from nw_activities.interactors.mixins.activity_group_association_mixin import \
    ActivityGroupAssociationMixin
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import ActivityGroupStorageInterface, \
    UserActivityGroupInstanceMetricTrackerDTO, \
    ActivityGroupCompletionMetricDTO, ActivityGroupFrequencyConfigDTO, \
    UserActivityGroupInstanceDTO


class ActivityGroupAssociationActivityInteractor(ActivityGroupAssociationMixin):

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        super().__init__(activity_group_storage)
        self.activity_group_storage = activity_group_storage

    def update_associations_completion_metrics_of_type_activity(
            self, user_activity_dto: UserActivityDTO):
        activity_group_ids = self._get_activity_group_ids(
            user_activity_dto.activity_name_enum)

        activity_group_frequency_config_dtos = \
            self.activity_group_storage.get_activity_groups_frequency_configs(
                activity_group_ids)

        user_activity_group_instance_dtos = \
            self.get_or_create_user_activity_group_instances_for_instance_type(
                user_activity_dto.user_id, activity_group_ids,
                activity_group_frequency_config_dtos,
                InstanceTypeEnum.DEFAULT.value)

        if not user_activity_group_instance_dtos:
            return

        activity_group_id_wise_completion_metric_dtos = \
            self.get_activity_group_id_wise_completion_metric_dtos(
                activity_group_ids)

        if not activity_group_id_wise_completion_metric_dtos:
            return

        updated_user_activity_group_instance_metric_tracker_dtos = \
            self.update_activity_groups_completion_metrics(
                activity_group_id_wise_completion_metric_dtos,
                user_activity_dto, user_activity_group_instance_dtos)

        completed_activity_group_ids = \
            self.update_user_activity_group_instance_completion_details(
                activity_group_id_wise_completion_metric_dtos,
                updated_user_activity_group_instance_metric_tracker_dtos,
                user_activity_group_instance_dtos)

        self._send_activity_group_completed_event(
            user_activity_dto.user_id, completed_activity_group_ids,
            activity_group_frequency_config_dtos)

        self._update_activity_group_association_type_completion_metrics(
            user_activity_dto.user_id, activity_group_ids)

        self._update_user_activity_group_instance_rewards(
            user_activity_dto.user_id, activity_group_ids)

    @atomic_transaction()
    def update_activity_groups_completion_metrics(
            self, activity_group_id_wise_completion_metric_dtos:
            Dict[str, List[ActivityGroupCompletionMetricDTO]],
            user_activity_dto: UserActivityDTO,
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO],
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

        updated_user_activity_group_instance_metric_tracker_dtos = \
            self._create_or_update_user_activity_group_instances_metric_tracker(
                activity_group_id_wise_completion_metric_dtos,
                ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto,
                activity_group_id_wise_user_activity_group_instance_id,
                user_activity_dto.resource_name_enum,
                user_activity_dto.resource_value)

        return updated_user_activity_group_instance_metric_tracker_dtos

    def _create_or_update_user_activity_group_instances_metric_tracker(
            self, activity_group_id_wise_completion_metric_dtos:
            Dict[str, List[ActivityGroupCompletionMetricDTO]],
            ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto:
            Dict[Tuple[str, str], UserActivityGroupInstanceMetricTrackerDTO],
            ag_id_wise_user_activity_group_instance_id: Dict[str, str],
            entity_id: str, value: float,
    ) -> List[UserActivityGroupInstanceMetricTrackerDTO]:
        user_activity_group_instance_metric_dtos_to_update = []
        user_activity_group_instance_metric_dtos_to_create = []
        for activity_group_id, completion_metric_dtos in \
                activity_group_id_wise_completion_metric_dtos.items():
            user_activity_completion_metric_dtos = \
                self._get_updated_user_activity_completion_metric_dtos(
                    activity_group_id,
                    ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto,
                    ag_id_wise_user_activity_group_instance_id,
                    completion_metric_dtos, entity_id, value)
            user_activity_group_instance_metric_dtos_to_create.extend(
                user_activity_completion_metric_dtos[0],
            )
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

    @staticmethod
    def _get_updated_user_activity_completion_metric_dtos(
            activity_group_id: str,
            ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto:
            Dict[Tuple[str, str], UserActivityGroupInstanceMetricTrackerDTO],
            ag_id_wise_user_activity_group_instance_id: Dict[str, str],
            completion_metric_dtos: List[ActivityGroupCompletionMetricDTO],
            entity_id: str, value: float,
    ) -> Tuple[List[UserActivityGroupInstanceMetricTrackerDTO],
               List[UserActivityGroupInstanceMetricTrackerDTO]]:
        from nw_activities.utils.generate_uuid import generate_uuid

        user_activity_group_instance_metric_dtos_to_create = []
        user_activity_group_instance_metric_dtos_to_update = []
        for dto in completion_metric_dtos:
            if dto.entity_id == entity_id:
                user_activity_group_instance_id = \
                    ag_id_wise_user_activity_group_instance_id[
                        activity_group_id]
                ag_completion_metric_id_agi_id_tuple = (
                    dto.id, user_activity_group_instance_id)
                user_agi_metric_tracker_dto = \
                    ag_completion_id_agi_id_wise_user_agi_metric_tracker_dto.get(
                        ag_completion_metric_id_agi_id_tuple)

                if user_agi_metric_tracker_dto:
                    user_agi_metric_tracker_dto.current_value += value
                    user_activity_group_instance_metric_dtos_to_update.append(
                        user_agi_metric_tracker_dto)
                else:
                    user_agi_metric_tracker_dto = \
                        UserActivityGroupInstanceMetricTrackerDTO(
                            id=generate_uuid(),
                            user_activity_group_instance_id=
                            user_activity_group_instance_id,
                            activity_group_completion_metric_id=dto.id,
                            current_value=value,
                            activity_group_optional_metric_id=None,
                        )
                    user_activity_group_instance_metric_dtos_to_create.append(
                        user_agi_metric_tracker_dto)

        return user_activity_group_instance_metric_dtos_to_create, \
            user_activity_group_instance_metric_dtos_to_update

    def _get_activity_group_ids(self, activity_id: str) -> List[str]:
        activity_group_association_dtos = self.activity_group_storage.\
            get_activity_group_associations_for_association_ids([activity_id])
        activity_group_ids = [
            dto.activity_group_id
            for dto in activity_group_association_dtos
        ]
        return activity_group_ids

    def _update_activity_group_association_type_completion_metrics(
            self, user_id: str, association_ids: List[str]):
        activity_group_association_dtos = self.activity_group_storage. \
            get_activity_group_associations_for_association_ids(association_ids)

        activity_group_ids = [dto.activity_group_id
                              for dto in activity_group_association_dtos]

        if not activity_group_ids:
            return

        from nw_activities.interactors.\
            update_activity_group_association_completion_metrics.activity_group\
            import ActivityGroupAssociationActivityGroupInteractor
        interactor = ActivityGroupAssociationActivityGroupInteractor(
            self.activity_group_storage)
        interactor.update_associations_completion_metrics_of_type_activity_group(
            user_id, activity_group_ids)

    def _update_user_activity_group_instance_rewards(
            self, user_id: str, activity_group_ids: List[str]):
        from nw_activities.interactors.\
            create_user_activity_group_instance_rewards import \
            CreateUserActivityGroupInstanceRewardInteractor
        interactor = CreateUserActivityGroupInstanceRewardInteractor(
            self.activity_group_storage)
        interactor.create_user_activity_group_instance_rewards(
            user_id, activity_group_ids)

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

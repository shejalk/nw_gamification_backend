from typing import List, Dict, Tuple

from ib_common.decorators.atomic_transaction import atomic_transaction

from nw_activities.constants.enum import InstanceTypeEnum
from nw_activities.interactors.dtos import UserActivityDTO
from nw_activities.interactors.mixins.activity_group_association_mixin import \
    ActivityGroupAssociationMixin
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import ActivityGroupStorageInterface, \
    ActivityGroupOptionalMetricDTO, UserActivityGroupInstanceDTO, \
    UserActivityGroupInstanceMetricTrackerDTO


class ActivityGroupAssociationActivityInteractor(
        ActivityGroupAssociationMixin):

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        super().__init__(activity_group_storage)
        self.activity_group_storage = activity_group_storage

    def update_associations_optional_metrics_of_type_activity(
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

        activity_group_id_wise_optional_metric_dtos = \
            self.get_activity_group_id_wise_optional_metric_dtos(
                activity_group_ids)

        if not activity_group_id_wise_optional_metric_dtos:
            return

        self.update_activity_groups_optional_metrics(
            activity_group_id_wise_optional_metric_dtos,
            user_activity_dto.resource_name_enum,
            user_activity_dto.resource_value,
            user_activity_group_instance_dtos)

    def _get_activity_group_ids(self, activity_id: str) -> List[str]:
        activity_group_association_dtos = self.activity_group_storage.\
            get_activity_group_associations_for_association_ids([activity_id])
        activity_group_ids = [
            dto.activity_group_id
            for dto in activity_group_association_dtos
        ]
        return activity_group_ids

    @atomic_transaction()
    def update_activity_groups_optional_metrics(
            self, activity_group_id_wise_optional_metric_dtos:
            Dict[str, List[ActivityGroupOptionalMetricDTO]],
            entity_id: str, entity_value: float,
            user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO],
    ) -> List[UserActivityGroupInstanceMetricTrackerDTO]:
        user_activity_group_instance_ids = \
            self.get_user_activity_group_instance_ids(
                user_activity_group_instance_dtos)

        user_ag_instance_metric_tracker_dtos = \
            self.get_user_activity_group_instances_metric_tracker(
                user_activity_group_instance_ids)

        ag_optional_id_agi_id_wise_user_agi_metric_tracker_dto = \
            self\
            .get_ag_optional_metric_id_agi_id_wise_user_agi_metric_tracker_dto(
                user_ag_instance_metric_tracker_dtos)

        activity_group_id_wise_user_activity_group_instance_id = \
            self.get_activity_group_id_wise_user_activity_group_instance_id(
                user_activity_group_instance_dtos)

        updated_user_activity_group_instance_metric_tracker_dtos = \
            self\
            ._create_or_update_user_activity_group_instances_metric_tracker(
                activity_group_id_wise_optional_metric_dtos,
                ag_optional_id_agi_id_wise_user_agi_metric_tracker_dto,
                activity_group_id_wise_user_activity_group_instance_id,
                entity_id, entity_value)

        return updated_user_activity_group_instance_metric_tracker_dtos

    def _create_or_update_user_activity_group_instances_metric_tracker(
            self, activity_group_id_wise_optional_metric_dtos:
            Dict[str, List[ActivityGroupOptionalMetricDTO]],
            ag_optional_id_agi_id_wise_user_agi_metric_tracker_dto:
            Dict[Tuple[str, str], UserActivityGroupInstanceMetricTrackerDTO],
            ag_id_wise_user_activity_group_instance_id: Dict[str, str],
            entity_id: str, value: float,
    ) -> List[UserActivityGroupInstanceMetricTrackerDTO]:
        user_activity_group_instance_metric_dtos_to_update = []
        user_activity_group_instance_metric_dtos_to_create = []
        for activity_group_id, optional_metric_dtos in \
                activity_group_id_wise_optional_metric_dtos.items():
            user_activity_optional_metric_dtos = \
                self._get_updated_user_activity_group_instance_metric_tracker(
                    activity_group_id,
                    ag_optional_id_agi_id_wise_user_agi_metric_tracker_dto,
                    ag_id_wise_user_activity_group_instance_id,
                    optional_metric_dtos, entity_id, value)
            user_activity_group_instance_metric_dtos_to_create.extend(
                user_activity_optional_metric_dtos[0],
            )
            user_activity_group_instance_metric_dtos_to_update.extend(
                user_activity_optional_metric_dtos[1],
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
    def _get_updated_user_activity_group_instance_metric_tracker(
            activity_group_id: str,
            ag_optional_id_agi_id_wise_user_agi_metric_tracker_dto:
            Dict[Tuple[str, str], UserActivityGroupInstanceMetricTrackerDTO],
            ag_id_wise_user_activity_group_instance_id: Dict[str, str],
            optional_metric_dtos: List[ActivityGroupOptionalMetricDTO],
            entity_id: str, value: float,
    ) -> Tuple[List[UserActivityGroupInstanceMetricTrackerDTO],
               List[UserActivityGroupInstanceMetricTrackerDTO]]:
        from nw_activities.utils.generate_uuid import generate_uuid

        user_activity_group_instance_metric_dtos_to_create = []
        user_activity_group_instance_metric_dtos_to_update = []
        for dto in optional_metric_dtos:
            if dto.entity_id == entity_id:
                user_activity_group_instance_id = \
                    ag_id_wise_user_activity_group_instance_id[
                        activity_group_id]
                ag_optional_metric_id_agi_id_tuple = (
                    dto.id, user_activity_group_instance_id)
                user_agi_metric_tracker_dto = \
                    ag_optional_id_agi_id_wise_user_agi_metric_tracker_dto.get(
                        ag_optional_metric_id_agi_id_tuple)

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
                            activity_group_completion_metric_id=None,
                            current_value=value,
                            activity_group_optional_metric_id=dto.id,
                        )
                    user_activity_group_instance_metric_dtos_to_create.append(
                        user_agi_metric_tracker_dto)

        return user_activity_group_instance_metric_dtos_to_create, \
            user_activity_group_instance_metric_dtos_to_update

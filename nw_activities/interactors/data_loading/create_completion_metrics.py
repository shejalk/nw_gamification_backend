from collections import defaultdict
from typing import List, Dict, Any

from nw_activities.adapters.service_adapter import get_service_adapter
from nw_activities.constants.enum import CompletionMetricEntityTypeEnum
from nw_activities.exceptions.custom_exceptions import \
    InvalidInputDataException
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import ActivityGroupStorageInterface, \
    CompletionMetricDTO


class CreateCompletionMetricInteractor:

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        self.activity_group_storage = activity_group_storage

    def create_completion_metrics(
            self, completion_metrics: List[Dict[str, Any]]):
        """
        :param completion_metrics: [{
            "id": string
            "entity_id": string
            "entity_type": string
            "value": float,
            "activity_group_ids: List[str]
        }]
        :type completion_metrics:
        :return:
        :rtype:
        """
        self._validate_completion_metrics(completion_metrics)

        completion_metric_dtos = [
            CompletionMetricDTO(
                id=each['id'],
                entity_id=each['entity_id'],
                entity_type=each['entity_type'],
                value=each['value'],
                activity_group_ids=each['activity_group_ids'],
            )
            for each in completion_metrics
        ]

        self.activity_group_storage.create_completion_metrics(
            completion_metric_dtos)

    def _validate_completion_metrics(
            self, completion_metrics: List[Dict[str, Any]]):
        invalid_completion_metric_ids = \
            self._get_invalid_completion_metric_ids(completion_metrics)

        completion_metric_id_wise_invalid_entity_details = \
            self._get_completion_metric_id_wise_invalid_entity_details(
                completion_metrics)

        completion_metric_id_wise_invalid_value = \
            self._get_completion_metric_id_wise_invalid_value(
                completion_metrics)

        activity_group_id_wise_invalid_completion_metric_ids = \
            self._get_activity_group_id_wise_invalid_completion_metric_ids(
                completion_metrics)

        invalid_activity_group_ids = self._get_invalid_activity_group_ids(
            completion_metrics)

        invalid_data = {}
        if invalid_completion_metric_ids:
            invalid_data['invalid_completion_metric_ids'] = \
                invalid_completion_metric_ids

        if completion_metric_id_wise_invalid_entity_details:
            invalid_data['completion_metric_id_wise_invalid_entity_details'] \
                = completion_metric_id_wise_invalid_entity_details

        if completion_metric_id_wise_invalid_value:
            invalid_data['completion_metric_id_wise_invalid_value'] = \
                completion_metric_id_wise_invalid_value

        if activity_group_id_wise_invalid_completion_metric_ids:
            invalid_data[
                "activity_group_id_wise_invalid_completion_metric_ids"] = \
                activity_group_id_wise_invalid_completion_metric_ids

        if invalid_activity_group_ids:
            invalid_data["invalid_activity_group_ids"] = \
                invalid_activity_group_ids

        if invalid_data:
            raise InvalidInputDataException(invalid_data)

    @staticmethod
    def _get_completion_metric_id_wise_invalid_value(
            completion_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        completion_metric_id_wise_invalid_value = {}
        for each in completion_metrics:
            if not each['value']:
                completion_metric_id_wise_invalid_value[each['id']] = \
                    each['value']
            else:
                if each['value'] < 0:
                    completion_metric_id_wise_invalid_value[each['id']] = \
                        each['value']
        return completion_metric_id_wise_invalid_value

    def _get_invalid_completion_metric_ids(
            self, completion_metrics: List[Dict[str, Any]]) -> List[str]:
        completion_metric_ids = [each['id'] for each in completion_metrics]
        existing_completion_metric_ids = \
            self.activity_group_storage.get_existing_completion_metric_ids(
                completion_metric_ids)
        invalid_completion_metric_ids = list(
            set(completion_metric_ids) & set(existing_completion_metric_ids),
        )
        return invalid_completion_metric_ids

    def _get_completion_metric_id_wise_invalid_entity_details(
            self, completion_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        invalid_resource_entity_ids = self._get_invalid_resource_entity_ids(
            completion_metrics)

        invalid_activity_group_association_entity_ids = \
            self._get_invalid_activity_group_association_entity_ids(
                completion_metrics)

        invalid_data = {}
        if invalid_resource_entity_ids:
            invalid_data["invalid_resource_entity_ids"] = \
                invalid_resource_entity_ids

        if invalid_activity_group_association_entity_ids:
            invalid_data["invalid_activity_group_association_entity_ids"] = \
                invalid_activity_group_association_entity_ids

        return invalid_data

    def _get_invalid_activity_group_association_entity_ids(
            self, completion_metrics: List[Dict[str, Any]]) -> List[str]:
        activity_group_association_entity_ids = [
            each['entity_id']
            for each in completion_metrics
            if each['entity_type'] ==
            CompletionMetricEntityTypeEnum.ACTIVITY_GROUP_ASSOCIATION.value
        ]

        existing_activity_group_association_ids = self.activity_group_storage.\
            get_existing_activity_group_association_ids(
                activity_group_association_entity_ids)

        invalid_activity_group_association_entity_ids = list(
            set(activity_group_association_entity_ids) -
            set(existing_activity_group_association_ids),
        )
        return invalid_activity_group_association_entity_ids

    def _get_invalid_resource_entity_ids(
            self, completion_metrics: List[Dict[str, Any]]) -> List[str]:
        resource_entity_ids = [
            each['entity_id']
            for each in completion_metrics
            if each['entity_type'] ==
            CompletionMetricEntityTypeEnum.RESOURCE.value
        ]

        existing_resource_ids = self._get_existing_resource_name_enums(
            resource_entity_ids)

        invalid_resource_entity_ids = list(
            set(resource_entity_ids) - set(existing_resource_ids),
        )

        return invalid_resource_entity_ids

    @staticmethod
    def _get_existing_resource_name_enums(
            resource_entity_ids: List[str]) -> List[str]:
        adapter = get_service_adapter()
        existing_resource_entity_ids = \
            adapter.resources.get_existing_resource_name_enums(
                resource_entity_ids)
        return existing_resource_entity_ids

    def _get_activity_group_id_wise_invalid_completion_metric_ids(
            self, completion_metrics: List[Dict[str, Any]]) -> \
            Dict[str, List[str]]:
        activity_group_id_wise_completion_metric_ids = defaultdict(list)
        for each in completion_metrics:
            for activity_group_id in each['activity_group_ids']:
                activity_group_id_wise_completion_metric_ids[
                    activity_group_id].append(each['id'])

        activity_group_ids = list(
            activity_group_id_wise_completion_metric_ids.keys())
        existing_activity_groups_completion_metric_dtos = \
            self.activity_group_storage.get_activity_groups_completion_metrics(
                activity_group_ids)

        existing_activity_group_id_wise_completion_metric_ids = \
            defaultdict(list)
        for dto in existing_activity_groups_completion_metric_dtos:
            existing_activity_group_id_wise_completion_metric_ids[
                dto.activity_group_id].append(dto.id)

        activity_group_id_wise_invalid_completion_metric_ids = {}
        for activity_group_id, completion_metric_ids in \
                activity_group_id_wise_completion_metric_ids.items():
            existing_completion_metric_ids = \
                existing_activity_group_id_wise_completion_metric_ids[
                    activity_group_id]
            invalid_completion_metric_ids = list(
                set(completion_metric_ids) & set(
                    existing_completion_metric_ids),
            )
            if invalid_completion_metric_ids:
                activity_group_id_wise_invalid_completion_metric_ids[
                    activity_group_id] = invalid_completion_metric_ids

        return activity_group_id_wise_invalid_completion_metric_ids

    def _get_invalid_activity_group_ids(
            self, completion_metrics: List[Dict[str, Any]]) -> List[str]:
        activity_group_ids = []
        for each in completion_metrics:
            activity_group_ids.extend(each['activity_group_ids'])

        existing_activity_group_ids = \
            self.activity_group_storage.get_existing_activity_group_ids(
                activity_group_ids)

        invalid_activity_group_ids = list(
            set(activity_group_ids) - set(existing_activity_group_ids),
        )

        return invalid_activity_group_ids

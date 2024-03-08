from collections import Counter
from typing import Dict, List, Any, Tuple

from nw_activities.constants.enum import ActivityGroupAssociationTypeEnum
from nw_activities.exceptions.custom_exceptions import InvalidInputDataException
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import ActivityGroupStorageInterface, \
    ActivityGroupAssociationDTO
from nw_activities.interactors.storage_interfaces.activity_storage_interface \
    import ActivityStorageInterface


class CreateActivityGroupAssociationInteractor:

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface,
                 activity_storage: ActivityStorageInterface):
        self.activity_group_storage = activity_group_storage
        self.activity_storage = activity_storage

    def create_activity_group_associations(
            self, activity_group_associations: List[Dict[str, str]]):
        """
        :param activity_group_associations: [{
            "id": "string",
            "activity_group_id": "string",
            "association_id": "string",
            "association_type": "string"
        }]
        :type activity_group_associations:
        :return:
        :rtype:
        """

        self._validate_activity_group_associations(activity_group_associations)

        activity_group_association_dtos = [
            self._convert_activity_group_association_to_dto(each)
            for each in activity_group_associations
        ]

        self.activity_group_storage.create_activity_group_associations(
            activity_group_association_dtos)

    def _validate_activity_group_associations(
            self, activity_group_associations: List[Dict[str, str]]):
        duplication_activity_group_association_data = \
            self._get_duplicate_activity_group_association_data(
                activity_group_associations)

        invalid_activity_group_association_ids = \
            self._get_invalid_activity_group_association_ids(
                activity_group_associations)

        invalid_activity_group_id_association_id_tuples = \
            self._get_invalid_activity_group_id_association_ids(
                activity_group_associations)

        invalid_activity_group_ids = self._get_invalid_activity_group_ids(
            activity_group_associations)

        invalid_association_data = self._get_invalid_association_data(
            activity_group_associations)

        invalid_data = {}
        if duplication_activity_group_association_data:
            invalid_data["duplication_activity_group_association_data"] = \
                duplication_activity_group_association_data

        if invalid_activity_group_id_association_id_tuples:
            invalid_data[
                "activity_group_id_association_ids_already_linked"
            ] = invalid_activity_group_id_association_id_tuples

        if invalid_activity_group_association_ids:
            invalid_data["invalid_activity_group_association_ids"] = \
                invalid_activity_group_association_ids

        if invalid_activity_group_ids:
            invalid_data["invalid_activity_group_ids"] = \
                invalid_activity_group_ids

        if invalid_association_data:
            invalid_data["invalid_association_data"] = invalid_association_data

        if invalid_data:
            raise InvalidInputDataException(invalid_data)

    def _get_invalid_activity_group_association_ids(
            self, activity_group_associations: List[Dict[str, str]]) -> \
            List[str]:
        activity_group_association_ids = [
            each["id"]
            for each in activity_group_associations
        ]

        existing_activity_group_association_dtos = \
            self.activity_group_storage.get_activity_group_associations(
                activity_group_association_ids)

        existing_activity_group_association_ids = [
            dto.id
            for dto in existing_activity_group_association_dtos
        ]

        invalid_activity_group_association_ids = list(
            set(existing_activity_group_association_ids) &
            set(activity_group_association_ids),
        )

        return invalid_activity_group_association_ids

    @staticmethod
    def _get_duplicate_activity_group_association_data(
            activity_group_associations: List[Dict[str, str]]) -> \
            Dict[str, Any]:
        activity_group_association_ids = [
            each["id"]
            for each in activity_group_associations
        ]

        duplication_activity_group_association_ids = [
            activity_group_association_id
            for activity_group_association_id, count in
            Counter(activity_group_association_ids).items() if count > 1
        ]

        duplication_activity_group_association_data = {}
        if duplication_activity_group_association_ids:
            duplication_activity_group_association_data[
                "duplication_activity_group_association_ids"] = \
                duplication_activity_group_association_ids

        activity_group_id_association_id_tuples = [
            (each["activity_group_id"], each["association_id"])
            for each in activity_group_associations
        ]

        duplication_activity_group_id_association_id_tuples = [
            activity_group_id_association_id
            for activity_group_id_association_id, count in
            Counter(activity_group_id_association_id_tuples).items()
            if count > 1
        ]

        if duplication_activity_group_id_association_id_tuples:
            duplication_activity_group_association_data[
                "duplication_activity_group_id_association_id_tuples"] = \
                duplication_activity_group_id_association_id_tuples

        return duplication_activity_group_association_data

    def _get_invalid_activity_group_id_association_ids(
            self, activity_group_associations: List[Dict[str, str]]) -> \
            List[Tuple[str, str]]:
        activity_group_ids = [
            each["activity_group_id"]
            for each in activity_group_associations
        ]
        existing_activity_group_association_dtos = self.activity_group_storage\
            .get_activity_group_associations_for_activity_group_ids(
                activity_group_ids)

        activity_group_id_association_id_tuples = [
            (each["activity_group_id"], each["association_id"])
            for each in activity_group_associations
        ]

        existing_activity_group_id_association_id_tuples = [
            (dto.activity_group_id, dto.association_id)
            for dto in existing_activity_group_association_dtos
        ]

        invalid_activity_group_id_association_id_tuples = list(
            set(activity_group_id_association_id_tuples) &
            set(existing_activity_group_id_association_id_tuples),
        )

        return invalid_activity_group_id_association_id_tuples

    def _get_invalid_activity_group_ids(
            self, activity_group_associations: List[Dict[str, str]]) -> \
            List[str]:
        activity_group_ids = [
            each["activity_group_id"]
            for each in activity_group_associations
        ]

        existing_activity_group_ids = \
            self.activity_group_storage.get_existing_activity_group_ids(
                activity_group_ids)

        invalid_activity_group_ids = list(
            set(activity_group_ids) - set(existing_activity_group_ids),
        )

        return invalid_activity_group_ids

    def _get_invalid_association_data(
            self, activity_group_associations: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        invalid_association_types = self._get_invalid_association_types(
            activity_group_associations)

        invalid_activity_type_association_ids = \
            self._get_invalid_activity_type_association_ids(
                activity_group_associations)

        invalid_activity_group_type_association_ids = \
            self._get_invalid_activity_group_type_association_ids(
                activity_group_associations)

        invalid_association_data = {}
        if invalid_association_types:
            invalid_association_data["invalid_association_types"] = \
                invalid_association_types

        if invalid_activity_type_association_ids:
            invalid_association_data["invalid_activity_type_association_ids"] \
                = invalid_activity_type_association_ids

        if invalid_activity_group_type_association_ids:
            invalid_association_data[
                "invalid_activity_group_type_association_ids"] = \
                invalid_activity_group_type_association_ids

        return invalid_association_data

    @staticmethod
    def _get_invalid_association_types(
            activity_group_associations: List[Dict[str, str]]) -> List[str]:
        association_types = [
            each["association_type"]
            for each in activity_group_associations
        ]
        invalid_association_types = list(
            set(association_types) -
            set(ActivityGroupAssociationTypeEnum.get_list_of_values()),
        )
        return invalid_association_types

    def _get_invalid_activity_type_association_ids(
            self, activity_group_associations: List[Dict[str, str]]) -> \
            List[str]:
        activity_type_association_ids = [
            each["association_id"]
            for each in activity_group_associations
            if each['association_type'] ==
            ActivityGroupAssociationTypeEnum.ACTIVITY.value
        ]

        existing_activity_type_association_ids = \
            self.activity_storage.get_existing_activity_name_enums(
                activity_type_association_ids)

        invalid_activity_type_association_ids = list(
            set(activity_type_association_ids) -
            set(existing_activity_type_association_ids),
        )
        return invalid_activity_type_association_ids

    def _get_invalid_activity_group_type_association_ids(
            self, activity_group_associations: List[Dict[str, str]]) -> \
            List[str]:
        activity_group_type_association_ids = [
            each["association_id"]
            for each in activity_group_associations
            if each['association_type'] ==
            ActivityGroupAssociationTypeEnum.ACTIVITY_GROUP.value
        ]

        existing_activity_group_type_association_ids = \
            self.activity_group_storage.get_existing_activity_group_ids(
                activity_group_type_association_ids)

        invalid_activity_group_type_association_ids = list(
            set(activity_group_type_association_ids) -
            set(existing_activity_group_type_association_ids),
        )
        return invalid_activity_group_type_association_ids

    @staticmethod
    def _convert_activity_group_association_to_dto(
            activity_group_association: Dict[str, Any]) -> \
            ActivityGroupAssociationDTO:
        return ActivityGroupAssociationDTO(
            id=activity_group_association['id'],
            activity_group_id=activity_group_association['activity_group_id'],
            association_id=activity_group_association['association_id'],
            association_type=activity_group_association['association_type'],
        )

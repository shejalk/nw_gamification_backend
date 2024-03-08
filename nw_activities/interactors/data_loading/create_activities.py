from collections import Counter
from typing import List, Dict

from nw_activities.exceptions.custom_exceptions import InvalidInputDataException
from nw_activities.interactors.storage_interfaces.activity_storage_interface \
    import ActivityStorageInterface, ActivityDTO


class CreateActivityInteractor:

    def __init__(self, activity_storage: ActivityStorageInterface):
        self.activity_storage = activity_storage

    def create_activities(self, activities: List[Dict[str, str]]):
        """
        :param activities: [{
            "name_enum": "string",
            "name": "string",
            "description": "string"
        }]
        :type activities: List[Dict[str, str]]
        :return:
        :rtype:
        """

        self._validate_activities(activities)

        activity_dtos = self._convert_activities_to_activity_dtos(activities)

        self.activity_storage.create_activities(activity_dtos)

    @staticmethod
    def _convert_activities_to_activity_dtos(
            activities: List[Dict[str, str]]) -> List[ActivityDTO]:
        activity_dtos = [
            ActivityDTO(
                name_enum=activity['name_enum'],
                name=activity['name'],
                description=activity['description']
                if activity['description'] else None,
            )
            for activity in activities
        ]
        return activity_dtos

    def _validate_activities(self, activities: List[Dict[str, str]]):
        activity_name_enums = [each['name_enum'] for each in activities]

        duplicate_activity_name_enums = [
            activity_name_enum for activity_name_enum, count in
            Counter(activity_name_enums).items() if count > 1
        ]

        existing_activity_name_enums = \
            self.activity_storage.get_existing_activity_name_enums(
                activity_name_enums)

        invalid_activity_name_enums = list(
            set(activity_name_enums) & set(existing_activity_name_enums),
        )

        invalid_data = {}
        if invalid_activity_name_enums:
            invalid_data["activity_name_enums_already_exists"] = \
                invalid_activity_name_enums

        if duplicate_activity_name_enums:
            invalid_data["duplicate_activity_name_enums"] = \
                duplicate_activity_name_enums

        if invalid_data:
            raise InvalidInputDataException(invalid_data)

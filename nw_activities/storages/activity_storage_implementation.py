import datetime
from typing import List

from nw_activities.interactors.dtos import UserActivityDTO
from nw_activities.interactors.storage_interfaces.activity_storage_interface \
    import ActivityStorageInterface, ActivityDTO
from nw_activities.models.activity import Activity
from nw_activities.models.user_activity import UserActivityLog


class ActivityStorageImplementation(ActivityStorageInterface):

    def is_valid_activity(self, activity_name_enum: str) -> bool:
        is_exists = Activity.objects.filter(
            name_enum=activity_name_enum).exists()
        return is_exists

    def create_user_activity_log(self, user_activity_dto: UserActivityDTO):
        UserActivityLog.objects.create(
            user_id=user_activity_dto.user_id,
            activity_id=user_activity_dto.activity_name_enum,
            entity_id=user_activity_dto.entity_id,
            entity_type=user_activity_dto.entity_type,
            resource_name_enum=user_activity_dto.resource_name_enum,
            resource_value=user_activity_dto.resource_value,
            transaction_type=user_activity_dto.transaction_type,
        )

    def create_activities(self, activity_dtos: List[ActivityDTO]):
        activities = [
            self._convert_activity_dto_to_object(dto)
            for dto in activity_dtos
        ]
        Activity.objects.bulk_create(activities)

    @staticmethod
    def _convert_activity_dto_to_object(activity_dto: ActivityDTO) -> Activity:
        return Activity(
            name_enum=activity_dto.name_enum,
            name=activity_dto.name,
            description=activity_dto.description,
        )

    def get_existing_activity_name_enums(
            self, activity_name_enums: List[str]) -> List[str]:
        existing_activity_name_enums = Activity.objects.filter(
            name_enum__in=activity_name_enums).values_list(
            'name_enum', flat=True)
        return list(existing_activity_name_enums)

    def get_user_activities(
            self, user_id: str, from_datetime: datetime.datetime,
            to_datetime: datetime.datetime) -> List[UserActivityDTO]:
        user_activities = UserActivityLog.objects.filter(
            user_id=user_id, creation_datetime__gte=from_datetime,
            creation_datetime__lte=to_datetime).order_by("creation_datetime")
        user_activity_dtos = [
            UserActivityDTO(
                user_id=user_activity.user_id,
                activity_name_enum=user_activity.activity_id,
                entity_id=user_activity.entity_id,
                entity_type=user_activity.entity_type,
                resource_name_enum=user_activity.resource_name_enum,
                resource_value=user_activity.resource_value,
                transaction_type=user_activity.transaction_type,
            )
            for user_activity in user_activities
        ]
        return user_activity_dtos

import pytest

from nw_activities.models import UserActivityLog
from nw_activities.storages.activity_storage_implementation import \
    ActivityStorageImplementation
from nw_activities.tests.factories.interactor_dtos import \
    UserActivityDTOFactory
from nw_activities.tests.factories.models import ActivityFactory


@pytest.mark.django_db
class TestCreateUserActivityLog:
    def test_creates_user_activity_logs(self):
        activity = ActivityFactory()
        user_activity_dto = UserActivityDTOFactory(
            activity_name_enum=activity.name_enum)
        storage = ActivityStorageImplementation()

        storage.create_user_activity_log(user_activity_dto)

        user_activity_log = UserActivityLog.objects.get(
            user_id=user_activity_dto.user_id)
        assert user_activity_dto.activity_name_enum == \
               user_activity_log.activity_id
        assert user_activity_dto.entity_id == user_activity_log.entity_id
        assert user_activity_dto.entity_type == user_activity_log.entity_type
        assert user_activity_dto.resource_name_enum == \
               user_activity_log.resource_name_enum
        assert user_activity_dto.resource_value == \
               user_activity_log.resource_value
        assert user_activity_dto.transaction_type == \
               user_activity_log.transaction_type

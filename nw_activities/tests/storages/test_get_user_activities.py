import datetime
import uuid

import pytest

from nw_activities.tests.factories.interactor_dtos import \
    UserActivityDTOFactory
from nw_activities.tests.factories.models import UserActivityLogFactory


@pytest.mark.django_db
class TestGetUserActivities:

    @pytest.fixture
    def common_setup(self):
        from nw_activities.storages.activity_storage_implementation import \
            ActivityStorageImplementation
        storage = ActivityStorageImplementation()
        return storage

    def test_returns_existing_activity_name_enums(self, common_setup):
        # Arrange
        storage = common_setup
        user_id = str(uuid.uuid4())
        from_datetime = datetime.datetime.now()
        to_datetime = datetime.datetime.now() + datetime.timedelta(hours=1)
        user_activities = \
            UserActivityLogFactory.create_batch(3, user_id=user_id)

        user_activity_dtos = [
            UserActivityDTOFactory(
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

        # Act
        response = storage.get_user_activities(
            user_id, from_datetime, to_datetime)

        # Assert
        assert user_activity_dtos == response

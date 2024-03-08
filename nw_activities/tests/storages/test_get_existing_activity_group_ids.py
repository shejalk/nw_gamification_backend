import uuid

import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import ActivityGroupFactory


@pytest.mark.django_db
class TestGetExistingActivityGroupIds:
    def test_returns_existing_activity_group_ids(self):
        ActivityGroupFactory()
        expected_response = [
            str(obj.id)
            for obj in ActivityGroupFactory.create_batch(size=2)
        ]
        activity_group_ids = expected_response + [str(uuid.uuid4())]
        storage = ActivityGroupStorageImplementation()

        response = storage.get_existing_activity_group_ids(activity_group_ids)

        assert sorted(response) == sorted(expected_response)

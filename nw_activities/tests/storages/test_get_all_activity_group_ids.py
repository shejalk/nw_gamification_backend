import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import ActivityGroupFactory


@pytest.mark.django_db
class TestGetAllActivityGroupIds:
    def test_returns_all_activity_group_ids(self):
        expected_response = [
            str(obj.id)
            for obj in ActivityGroupFactory.create_batch(size=2)
        ]
        storage = ActivityGroupStorageImplementation()

        response = storage.get_all_activity_group_ids()

        assert sorted(response) == sorted(expected_response)

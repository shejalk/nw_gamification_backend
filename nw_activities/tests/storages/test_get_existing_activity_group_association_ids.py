import uuid

import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import \
    ActivityGroupAssociationFactory


@pytest.mark.django_db
class TestGetExistingActivityGroupAssociationIds:
    def test_returns_existing_activity_group_association_ids(self):
        ActivityGroupAssociationFactory()
        expected_response = [
            str(obj.id)
            for obj in ActivityGroupAssociationFactory.create_batch(size=2)
        ]
        activity_group_association_ids = \
            expected_response + [str(uuid.uuid4())]
        storage = ActivityGroupStorageImplementation()

        response = storage.get_existing_activity_group_association_ids(
            activity_group_association_ids)

        assert sorted(response) == sorted(expected_response)

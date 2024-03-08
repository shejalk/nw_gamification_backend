import pytest

from nw_activities.storages.activity_storage_implementation import \
    ActivityStorageImplementation
from nw_activities.tests.factories.models import ActivityFactory


@pytest.mark.django_db
class TestGetExistingActivityNameEnums:
    def test_returns_existing_activity_name_enums(self):
        ActivityFactory.create_batch(size=3)
        activity_name_enums = [
            "name_enum_1", "name_enum_2", "name_enum_10",
        ]
        expected_response = activity_name_enums[:2]
        storage = ActivityStorageImplementation()

        response = storage.get_existing_activity_name_enums(
            activity_name_enums)

        assert sorted(expected_response) == sorted(response)

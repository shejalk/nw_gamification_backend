import pytest

from nw_activities.storages.activity_storage_implementation import \
    ActivityStorageImplementation
from nw_activities.tests.factories.models import ActivityFactory


@pytest.mark.django_db
class TestIsValidActivity:
    def test_when_activity_is_valid_returns_true(self):
        ActivityFactory()
        activity_name_enum = "name_enum_1"
        expected_response = True
        storage = ActivityStorageImplementation()

        response = storage.is_valid_activity(activity_name_enum)

        assert expected_response == response

    def test_when_activity_is_invalid_returns_false(self):
        ActivityFactory()
        activity_name_enum = "name_enum_2"
        expected_response = False
        storage = ActivityStorageImplementation()

        response = storage.is_valid_activity(activity_name_enum)

        assert expected_response == response

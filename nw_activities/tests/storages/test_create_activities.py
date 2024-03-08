import pytest

from nw_activities.models import Activity
from nw_activities.storages.activity_storage_implementation import \
    ActivityStorageImplementation
from nw_activities.tests.factories.storage_dtos import ActivityDTOFactory


@pytest.mark.django_db
class TestCreateActivities:
    def test_creates_activities(self):
        activity_dtos = [
            ActivityDTOFactory(), ActivityDTOFactory(),
        ]
        storage = ActivityStorageImplementation()

        storage.create_activities(activity_dtos)

        activity_name_enum_wise_obj = {
            str(obj.name_enum): obj
            for obj in Activity.objects.all()
        }
        for activity_dto in activity_dtos:
            activity_obj = activity_name_enum_wise_obj[activity_dto.name_enum]
            assert activity_dto.name == activity_obj.name
            assert activity_dto.description == activity_obj.description

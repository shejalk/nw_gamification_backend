import pytest

from nw_activities.models import UserActivityGroupInstance
from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import \
    ActivityGroupFactory
from nw_activities.tests.factories.storage_dtos import \
    UserActivityGroupInstanceDTOFactory


@pytest.mark.django_db
class TestCreateUserActivityGroupInstances:
    def test_creates_user_activity_group_instances(self):
        activity_groups = ActivityGroupFactory.create_batch(size=2)
        user_activity_group_instance_dtos = [
            UserActivityGroupInstanceDTOFactory(
                activity_group_id=str(activity_group.id),
            )
            for activity_group in activity_groups
        ]
        storage = ActivityGroupStorageImplementation()

        storage.create_user_activity_group_instances(
            user_activity_group_instance_dtos)

        user_activity_group_instance_id_wise_obj = {
            str(obj.id): obj
            for obj in UserActivityGroupInstance.objects.all()
        }
        for dto in user_activity_group_instance_dtos:
            obj = user_activity_group_instance_id_wise_obj[dto.id]
            assert dto.instance_identifier == obj.instance_identifier
            assert dto.instance_type == obj.instance_type
            assert dto.user_id == obj.user_id
            assert dto.activity_group_id == str(obj.activity_group_id)
            assert dto.completion_percentage == obj.completion_percentage
            assert dto.completion_status == obj.completion_status

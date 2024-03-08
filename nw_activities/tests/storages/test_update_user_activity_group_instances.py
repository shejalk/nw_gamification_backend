import pytest

from nw_activities.models import UserActivityGroupInstance
from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import \
    UserActivityGroupInstanceFactory
from nw_activities.tests.factories.storage_dtos import \
    UserActivityGroupInstanceDTOFactory


@pytest.mark.django_db
class TestUpdateUserActivityGroupInstances:
    @pytest.fixture
    def setup_data(self):
        user_activity_group_instances = UserActivityGroupInstanceFactory. \
            create_batch(size=2)
        UserActivityGroupInstanceFactory()
        user_activity_group_instance_dtos = [
            UserActivityGroupInstanceDTOFactory(
                id=str(obj.id),
                activity_group_id=str(obj.activity_group_id),
            )
            for obj in user_activity_group_instances
        ]

        return user_activity_group_instance_dtos

    def test_updates_user_activity_group_instances(self, setup_data):
        user_activity_group_instance_dtos = setup_data
        storage = ActivityGroupStorageImplementation()

        storage.update_user_activity_group_instances(
            user_activity_group_instance_dtos)

        user_activity_group_instance_id_wise_obj = {
            str(obj.id): obj
            for obj in UserActivityGroupInstance.objects.all()
        }
        for dto in user_activity_group_instance_dtos:
            obj = user_activity_group_instance_id_wise_obj[dto.id]
            assert dto.instance_type == obj.instance_type
            assert dto.completion_percentage == obj.completion_percentage
            assert dto.completion_status == obj.completion_status

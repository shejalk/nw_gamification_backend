import uuid

import pytest

from nw_activities.models import UserActivityGroupInstance
from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import ActivityGroupFactory, \
    UserActivityGroupInstanceFactory


@pytest.mark.django_db
class TestDeleteUserActivityGroupInstances:
    def test_delete_user_activity_group_instances(self):
        activity_group = ActivityGroupFactory()
        user_activity_group_instance_ids = [
            str(uuid.uuid4()), str(uuid.uuid4()),
        ]
        user_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        UserActivityGroupInstanceFactory.create(
            activity_group=activity_group,
            user_id=user_ids[0],
            id=user_activity_group_instance_ids[0],
        )
        UserActivityGroupInstanceFactory.create(
            activity_group=activity_group,
            user_id=user_ids[1],
            id=user_activity_group_instance_ids[1],
        )

        storage = ActivityGroupStorageImplementation()
        storage.delete_user_activity_group_instances(
            user_activity_group_instance_ids)

        response = UserActivityGroupInstance.objects.filter(
            id__in=user_activity_group_instance_ids).exists()

        assert response is False

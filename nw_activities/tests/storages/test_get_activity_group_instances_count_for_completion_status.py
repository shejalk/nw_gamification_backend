import uuid

import pytest

from nw_activities.constants.enum import CompletionStatusEnum
from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import ActivityGroupFactory, \
    UserActivityGroupInstanceFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupInstanceCountDTOFactory


@pytest.mark.django_db
class TestGetActivityGroupInstancesCountForCompletionStatus:
    @pytest.fixture
    def setup_data(self):
        user_id = str(uuid.uuid4())
        activity_groups = [
            ActivityGroupFactory(), ActivityGroupFactory(),
        ]
        _ = [
            UserActivityGroupInstanceFactory(
                user_id=user_id, activity_group=activity_groups[0],
                completion_status=CompletionStatusEnum.COMPLETED.value,
            ),
            UserActivityGroupInstanceFactory(
                user_id=user_id, activity_group=activity_groups[1],
                completion_status=CompletionStatusEnum.COMPLETED.value,
            ),
            UserActivityGroupInstanceFactory(
                user_id=user_id, activity_group=activity_groups[1],
                completion_status=CompletionStatusEnum.COMPLETED.value,
            ),
            UserActivityGroupInstanceFactory(
                user_id=user_id, activity_group=activity_groups[0],
                completion_status=CompletionStatusEnum.IN_PROGRESS.value,
            ),
            UserActivityGroupInstanceFactory(
                user_id=user_id, activity_group=activity_groups[1],
                completion_status=CompletionStatusEnum.YET_TO_START.value,
            ),
        ]

        expected_response = [
            ActivityGroupInstanceCountDTOFactory(
                activity_group_id=str(activity_groups[0].id),
            ),
            ActivityGroupInstanceCountDTOFactory(
                activity_group_id=str(activity_groups[1].id),
            ),
        ]
        activity_group_ids = [str(obj.id) for obj in activity_groups]

        return user_id, activity_group_ids, expected_response

    def test_returns_activity_group_instances_count_dtos(self, setup_data):
        user_id, activity_group_ids, expected_response = setup_data
        completion_status = CompletionStatusEnum.COMPLETED.value
        storage = ActivityGroupStorageImplementation()

        response = storage.\
            get_activity_group_instances_count_for_completion_status(
                user_id, activity_group_ids, completion_status,
            )

        assert len(expected_response) == len(response)
        for dto in response:
            assert dto in expected_response

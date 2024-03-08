import uuid

import pytest

from nw_activities.constants.enum import CompletionStatusEnum, \
    InstanceTypeEnum
from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import \
    UserActivityGroupInstanceFactory, ActivityGroupFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupInstanceIdentifierDTOFactory


@pytest.mark.django_db
class TestGetAGIUserIdsForInstanceTypesCompletionTypes:
    @pytest.fixture
    def setup_data(self):
        user_ids = [str(uuid.uuid4()) for each in range(6)]
        activity_groups = ActivityGroupFactory.create_batch(size=2)
        instance_identifiers = [
            "2022-08-1 09:00:00#2022-08-1 21:00:00",
            "2022-08-2 09:00:00#2022-08-2 21:00:00",
            "2022-08-3 09:00:00#2022-08-3 21:00:00"
        ]
        user_activity_group_instances = [  # pylint: disable=W0612
            UserActivityGroupInstanceFactory(
                user_id=user_ids[0],
                activity_group=activity_groups[0],
                instance_type=InstanceTypeEnum.DEFAULT.value,
                completion_status=CompletionStatusEnum.COMPLETED.value,
                instance_identifier=instance_identifiers[0]),
            UserActivityGroupInstanceFactory(
                user_id=user_ids[1],
                activity_group=activity_groups[1],
                instance_type=InstanceTypeEnum.DEFAULT.value,
                completion_status=CompletionStatusEnum.COMPLETED.value,
                instance_identifier=instance_identifiers[1]),
            UserActivityGroupInstanceFactory(
                user_id=user_ids[2],
                activity_group=activity_groups[1],
                instance_type=InstanceTypeEnum.DEFAULT.value,
                completion_status=CompletionStatusEnum.COMPLETED.value,
                instance_identifier=instance_identifiers[2]),
            UserActivityGroupInstanceFactory(
                user_id=user_ids[2],
                activity_group=activity_groups[1],
                instance_type=InstanceTypeEnum.NO_ACTIVITY.value,
                completion_status=CompletionStatusEnum.YET_TO_START.value,
                instance_identifier=instance_identifiers[1]),
            UserActivityGroupInstanceFactory(
                user_id=user_ids[2],
                activity_group=activity_groups[1],
                instance_type=InstanceTypeEnum.NO_ACTIVITY.value,
                completion_status=CompletionStatusEnum.YET_TO_START.value,
                instance_identifier=instance_identifiers[0]),
            UserActivityGroupInstanceFactory(
                user_id=user_ids[3],
                activity_group=activity_groups[1],
                instance_type=InstanceTypeEnum.NO_ACTIVITY.value,
                completion_status=CompletionStatusEnum.YET_TO_START.value,
                instance_identifier=instance_identifiers[2]),
            UserActivityGroupInstanceFactory(
                user_id=user_ids[3],
                activity_group=activity_groups[0],
                instance_type=InstanceTypeEnum.DEFAULT.value,
                completion_status=CompletionStatusEnum.YET_TO_START.value,
                instance_identifier=instance_identifiers[1]),
        ]

        activity_group_instance_identifier_dtos = [
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=str(activity_groups[0].id),
                instance_identifier=instance_identifiers[0],
            ),
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=str(activity_groups[1].id),
                instance_identifier=instance_identifiers[1],
            ),
        ]

        expected_response = user_ids[:2]

        return user_ids, activity_group_instance_identifier_dtos, \
            expected_response

    def test_get_agi_user_ids_for_instance_types_completion_types(
            self, setup_data):
        # arrange
        user_ids, activity_group_instance_identifier_dtos, \
            expected_response = setup_data
        storage = ActivityGroupStorageImplementation()

        # act
        response = storage.get_agi_user_ids_for_instance_types_completion_types(
            activity_group_instance_identifier_dtos,
            [InstanceTypeEnum.DEFAULT.value], user_ids,
            [CompletionStatusEnum.COMPLETED.value])

        # assert
        assert response == expected_response

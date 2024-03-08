import uuid

import pytest

from nw_activities.constants.enum import InstanceTypeEnum
from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import \
    UserActivityGroupInstanceFactory, ActivityGroupFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupInstanceIdentifierDTOFactory, \
    UserActivityGroupInstanceDTOFactory


@pytest.mark.django_db
class TestGetUserActivityGroupInstancesOfGivenTypes:
    @pytest.fixture
    def setup_data(self):
        user_id = str(uuid.uuid4)
        activity_groups = ActivityGroupFactory.create_batch(size=2)
        user_activity_group_instances = [
            UserActivityGroupInstanceFactory(
                user_id=user_id,
                activity_group=activity_groups[0],
                instance_type=InstanceTypeEnum.FREEZE.value),

            UserActivityGroupInstanceFactory(
                user_id=user_id,
                activity_group=activity_groups[1]),
            UserActivityGroupInstanceFactory(
                user_id=user_id,
                activity_group=activity_groups[0]),
            UserActivityGroupInstanceFactory(
                user_id=user_id,
                activity_group=activity_groups[1]),
            UserActivityGroupInstanceFactory(
                instance_identifier="2022-08-1 09:00:00#2022-08-1 "
                                    "21:00:00",
                activity_group=activity_groups[0]),
            UserActivityGroupInstanceFactory(
                instance_identifier="2022-08-2 09:00:00#2022-08-2 "
                                    "21:00:00",
                activity_group=activity_groups[1]),
        ]

        activity_group_instance_identifier_dtos = [
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=str(activity_groups[0].id),
                instance_identifier="2022-08-1 09:00:00#2022-08-1 "
                                    "21:00:00",
            ),
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=str(activity_groups[1].id),
                instance_identifier="2022-08-2 09:00:00#2022-08-2 "
                                    "21:00:00",
            ),
        ]

        expected_response = [
            UserActivityGroupInstanceDTOFactory(
                id=str(user_activity_group_instance.id),
                user_id=user_activity_group_instance.user_id,
                instance_identifier=
                user_activity_group_instance.instance_identifier,
                instance_type=user_activity_group_instance.instance_type,
                activity_group_id=
                str(user_activity_group_instance.activity_group_id),
                completion_percentage=
                user_activity_group_instance.completion_percentage,
                completion_status=
                user_activity_group_instance.completion_status,
            )
            for user_activity_group_instance in
            user_activity_group_instances[:1]
        ]

        return user_id, activity_group_instance_identifier_dtos, \
            expected_response

    def test_returns_user_activity_group_instances(self, setup_data):
        user_id, activity_group_instance_identifier_dtos, expected_response =\
            setup_data
        storage = ActivityGroupStorageImplementation()
        instance_types = [InstanceTypeEnum.FREEZE.value]

        response = storage.get_user_activity_group_instances_of_given_types(
            user_id, activity_group_instance_identifier_dtos, instance_types)

        assert len(expected_response) == len(response)
        for dto in response:
            assert dto in expected_response

    def test_returns_empty_list(self, setup_data):
        user_id = str(uuid.uuid4())
        activity_group_instance_identifier_dtos, expected_response = [], []
        storage = ActivityGroupStorageImplementation()
        instance_types = [InstanceTypeEnum.FREEZE.value]

        response = storage.get_user_activity_group_instances_of_given_types(
            user_id, activity_group_instance_identifier_dtos, instance_types)

        assert len(expected_response) == len(response)
        for dto in response:
            assert dto in expected_response

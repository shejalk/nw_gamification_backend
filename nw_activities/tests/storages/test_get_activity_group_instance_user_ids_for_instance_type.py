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
class TestGetActivityGroupInstancesUserIds:
    @pytest.fixture
    def setup_data(self):
        activity_groups = ActivityGroupFactory.create_batch(size=2)
        user_ids = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        instance_identifiers = [
            "2022-08-1 09:00:00#2022-08-1 21:00:00",
            "2022-08-2 09:00:00#2022-08-2 21:00:00",
        ]
        user_activity_group_instances = [
            UserActivityGroupInstanceFactory(
                activity_group=activity_groups[0],
                instance_type=InstanceTypeEnum.DEFAULT.value,
                user_id=user_ids[0],
                instance_identifier=instance_identifiers[0],
            ),
            UserActivityGroupInstanceFactory(
                activity_group=activity_groups[1],
                instance_type=InstanceTypeEnum.LEISURE.value,
                user_id=user_ids[0],
                instance_identifier=instance_identifiers[1],
            ),
            UserActivityGroupInstanceFactory(
                activity_group=activity_groups[0],
                instance_type=InstanceTypeEnum.LEISURE.value,
                user_id=user_ids[1],
                instance_identifier=instance_identifiers[0],
            ),
            UserActivityGroupInstanceFactory(
                activity_group=activity_groups[1],
                instance_type=InstanceTypeEnum.PAUSED.value,
                user_id=user_ids[1],
                instance_identifier=instance_identifiers[1],
            ),
            UserActivityGroupInstanceFactory(
                activity_group=activity_groups[0],
                instance_type=InstanceTypeEnum.PAUSED.value,
                user_id=user_ids[2],
                instance_identifier=instance_identifiers[0],
            ),
            UserActivityGroupInstanceFactory(
                activity_group=activity_groups[1],
                instance_type=InstanceTypeEnum.DEFAULT.value,
                user_id=user_ids[2],
                instance_identifier=instance_identifiers[1],
            ),
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

        user_activity_group_instance_dtos = [
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
            for user_activity_group_instance in user_activity_group_instances
        ]

        return activity_group_instance_identifier_dtos, \
            user_activity_group_instance_dtos

    def test_returns_default_instance_type_user_ids(self, setup_data):
        activity_group_instance_identifier_dtos, \
            user_activity_group_instance_dtos = setup_data
        storage = ActivityGroupStorageImplementation()

        expected_response = [user_activity_group_instance_dtos[0].user_id,
                             user_activity_group_instance_dtos[-1].user_id]

        response = \
            storage.get_activity_group_instance_user_ids_for_instance_type(
                activity_group_instance_identifier_dtos,
                InstanceTypeEnum.DEFAULT.value)

        assert len(expected_response) == len(response)
        for dto in expected_response:
            assert dto in response

    def test_returns_paused_instance_type_user_ids(self, setup_data):
        activity_group_instance_identifier_dtos, \
            user_activity_group_instance_dtos = setup_data
        storage = ActivityGroupStorageImplementation()

        expected_response = [user_activity_group_instance_dtos[3].user_id,
                             user_activity_group_instance_dtos[4].user_id]

        response = \
            storage.get_activity_group_instance_user_ids_for_instance_type(
                activity_group_instance_identifier_dtos,
                InstanceTypeEnum.PAUSED.value)

        assert len(expected_response) == len(response)
        for dto in expected_response:
            assert dto in response

    def test_returns_leisure_instance_type_user_ids(self, setup_data):
        activity_group_instance_identifier_dtos, \
            user_activity_group_instance_dtos = setup_data
        storage = ActivityGroupStorageImplementation()

        expected_response = [user_activity_group_instance_dtos[1].user_id,
                             user_activity_group_instance_dtos[2].user_id]

        response = \
            storage.get_activity_group_instance_user_ids_for_instance_type(
                activity_group_instance_identifier_dtos,
                InstanceTypeEnum.LEISURE.value)

        assert len(expected_response) == len(response)
        for dto in expected_response:
            assert dto in response

    def test_returns_empty_list(self):
        activity_group_instance_identifier_dtos, expected_response = [], []
        storage = ActivityGroupStorageImplementation()

        response = \
            storage.get_activity_group_instance_user_ids_for_instance_type(
                activity_group_instance_identifier_dtos,
                InstanceTypeEnum.DEFAULT.value)

        assert len(expected_response) == len(response)

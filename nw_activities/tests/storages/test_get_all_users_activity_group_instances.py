import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import \
    UserActivityGroupInstanceFactory, ActivityGroupFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupInstanceIdentifierDTOFactory, \
    UserActivityGroupInstanceDTOFactory


@pytest.mark.django_db
class TestGetAllUsersActivityGroupInstances:
    @pytest.fixture
    def setup_data(self):
        activity_groups = ActivityGroupFactory.create_batch(size=2)
        user_activity_group_instances = [
            UserActivityGroupInstanceFactory(
                activity_group=activity_groups[0]),
            UserActivityGroupInstanceFactory(
                activity_group=activity_groups[1]),
            UserActivityGroupInstanceFactory(
                activity_group=activity_groups[0]),
            UserActivityGroupInstanceFactory(
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
            user_activity_group_instances[:2]
        ]

        return activity_group_instance_identifier_dtos, expected_response

    def test_returns_all_users_activity_group_instances(self, setup_data):
        activity_group_instance_identifier_dtos, expected_response = setup_data
        storage = ActivityGroupStorageImplementation()

        response = storage.get_all_users_activity_group_instances(
            activity_group_instance_identifier_dtos)

        assert len(expected_response) == len(response)
        for dto in response:
            assert dto in expected_response

    def test_returns_empty_list(self):
        activity_group_instance_identifier_dtos, expected_response = [], []
        storage = ActivityGroupStorageImplementation()

        response = storage.get_all_users_activity_group_instances(
            activity_group_instance_identifier_dtos)

        assert len(expected_response) == len(response)
        for dto in response:
            assert dto in expected_response

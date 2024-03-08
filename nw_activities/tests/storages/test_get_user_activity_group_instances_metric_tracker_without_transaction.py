import uuid

import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import \
    UserActivityGroupInstanceMetricTrackerFactory
from nw_activities.tests.factories.storage_dtos import \
    UserActivityGroupInstanceMetricTrackerDTOFactory


@pytest.mark.django_db
class TestGetUserActivityGroupInstancesMetricTrackerWithoutTransaction:
    @pytest.fixture
    def setup_data(self):
        user_activity_group_instance_metric_trackers = [
            UserActivityGroupInstanceMetricTrackerFactory(),
            UserActivityGroupInstanceMetricTrackerFactory(),
        ]
        UserActivityGroupInstanceMetricTrackerFactory()

        user_activity_group_instance_ids = [
            str(obj.user_activity_group_instance_id)
            for obj in user_activity_group_instance_metric_trackers
        ]

        expected_response = [
            UserActivityGroupInstanceMetricTrackerDTOFactory(
                id=str(obj.id),
                user_activity_group_instance_id=
                str(obj.user_activity_group_instance_id),
                activity_group_completion_metric_id=
                str(obj.activity_group_completion_metric_id),
                current_value=round(obj.current_value, 2),
            )
            for obj in user_activity_group_instance_metric_trackers
        ]
        user_activity_group_instance_ids += [str(uuid.uuid4())]

        return user_activity_group_instance_ids, expected_response

    def test_returns_user_activity_group_instance_metric_tracker_dtos(
            self, setup_data):
        user_activity_group_instance_ids, expected_response = setup_data
        storage = ActivityGroupStorageImplementation()

        response = storage.\
            get_user_activity_group_instances_metric_tracker_without_transaction(
                user_activity_group_instance_ids,
            )

        assert len(expected_response) == len(response)
        for dto in response:
            assert dto in expected_response

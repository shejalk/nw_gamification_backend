import factory
import pytest

from nw_activities.models import UserActivityGroupInstanceMetricTracker
from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import \
    UserActivityGroupInstanceMetricTrackerFactory
from nw_activities.tests.factories.storage_dtos import \
    UserActivityGroupInstanceMetricTrackerDTOFactory


@pytest.mark.django_db
class TestUpdateUserActivityGroupInstancesMetricTracker:
    @pytest.fixture
    def setup_data(self):
        UserActivityGroupInstanceMetricTrackerFactory()
        user_activity_group_instance_metrics = \
            UserActivityGroupInstanceMetricTrackerFactory.create_batch(size=2)
        user_activity_group_instance_metric_dtos = [
            UserActivityGroupInstanceMetricTrackerDTOFactory(
                id=str(obj.id),
                user_activity_group_instance_id=
                str(obj.user_activity_group_instance_id),
                activity_group_completion_metric_id=
                str(obj.activity_group_completion_metric_id),
                current_value=factory.Iterator([10.0, 20.0]),
            )
            for obj in user_activity_group_instance_metrics
        ]

        return user_activity_group_instance_metric_dtos

    def test_updates_user_activity_group_instances_metric_tracker(
            self, setup_data):
        user_activity_group_instance_metric_dtos = setup_data
        storage = ActivityGroupStorageImplementation()

        storage.update_user_activity_group_instances_metric_tracker(
            user_activity_group_instance_metric_dtos)

        for dto in user_activity_group_instance_metric_dtos:
            actual_value = UserActivityGroupInstanceMetricTracker.objects\
                .get(id=dto.id).current_value
            assert dto.current_value == actual_value

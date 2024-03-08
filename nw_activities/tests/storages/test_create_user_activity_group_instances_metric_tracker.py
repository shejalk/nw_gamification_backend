import pytest

from nw_activities.models import UserActivityGroupInstanceMetricTracker
from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import \
    UserActivityGroupInstanceFactory, \
    CompletionMetricFactory
from nw_activities.tests.factories.storage_dtos import \
    UserActivityGroupInstanceMetricTrackerDTOFactory


@pytest.mark.django_db
class TestCreateUserActivityGroupInstancesMetricTracker:
    @pytest.fixture
    def setup_data(self):
        user_activity_group_instances = \
            UserActivityGroupInstanceFactory.create_batch(size=2)
        activity_group_completion_metrics = \
            CompletionMetricFactory.create_batch(size=2)

        user_activity_group_instance_metric_dtos = [
            UserActivityGroupInstanceMetricTrackerDTOFactory(
                user_activity_group_instance_id=
                str(user_activity_group_instances[0].id),
                activity_group_completion_metric_id=
                str(activity_group_completion_metrics[0].id),
            ),
            UserActivityGroupInstanceMetricTrackerDTOFactory(
                user_activity_group_instance_id=
                str(user_activity_group_instances[1].id),
                activity_group_completion_metric_id=
                str(activity_group_completion_metrics[1].id),
            ),
        ]

        return user_activity_group_instance_metric_dtos

    def test_creates_user_activity_group_instances_metric_tracker(
            self, setup_data):
        user_activity_group_instance_metric_dtos = setup_data
        storage = ActivityGroupStorageImplementation()

        storage.create_user_activity_group_instances_metric_tracker(
            user_activity_group_instance_metric_dtos)

        user_activity_group_instance_metric_tracker_id_wise_obj = {
            str(obj.id): obj
            for obj in UserActivityGroupInstanceMetricTracker.objects.all()
        }
        for dto in user_activity_group_instance_metric_dtos:
            obj = user_activity_group_instance_metric_tracker_id_wise_obj[
                dto.id]
            assert dto.user_activity_group_instance_id == str(
                obj.user_activity_group_instance_id)
            assert dto.activity_group_completion_metric_id == str(
                obj.activity_group_completion_metric_id)

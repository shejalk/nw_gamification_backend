import uuid

import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import ActivityGroupConfigFactory, \
    CompletionMetricFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupCompletionMetricDTOFactory


@pytest.mark.django_db
class TestGetActivityGroupsCompletionMetrics:
    @pytest.fixture
    def setup_data(self):
        activity_groups = [
            ActivityGroupConfigFactory(),
            ActivityGroupConfigFactory(),
        ]
        ActivityGroupConfigFactory()
        completion_metrics = [
            CompletionMetricFactory(), CompletionMetricFactory(),
            CompletionMetricFactory(),
        ]
        activity_groups[0].completion_metric.add(
            completion_metrics[0], completion_metrics[1])
        activity_groups[1].completion_metric.add(completion_metrics[2])
        activity_group_ids = [
            str(activity_group.activity_group_id)
            for activity_group in activity_groups
        ]
        expected_response = [
            ActivityGroupCompletionMetricDTOFactory(
                id=str(completion_metrics[0].id),
                activity_group_id=activity_group_ids[0],
                entity_id=str(completion_metrics[0].entity_id),
                entity_type=completion_metrics[0].entity_type,
            ),
            ActivityGroupCompletionMetricDTOFactory(
                id=str(completion_metrics[1].id),
                activity_group_id=activity_group_ids[0],
                entity_id=str(completion_metrics[1].entity_id),
                entity_type=completion_metrics[1].entity_type,
            ),
            ActivityGroupCompletionMetricDTOFactory(
                id=str(completion_metrics[2].id),
                activity_group_id=activity_group_ids[1],
                entity_id=str(completion_metrics[2].entity_id),
                entity_type=completion_metrics[2].entity_type,
            ),
        ]
        activity_group_ids += [str(uuid.uuid4())]

        return activity_group_ids, expected_response

    def test_returns_activity_group_completion_metrics(self, setup_data):
        activity_group_ids, expected_response = setup_data
        storage = ActivityGroupStorageImplementation()

        response = storage.get_activity_groups_completion_metrics(
            activity_group_ids)

        assert len(expected_response) == len(response)
        for dto in response:
            assert dto in expected_response

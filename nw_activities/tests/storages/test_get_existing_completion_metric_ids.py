import uuid

import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import CompletionMetricFactory


@pytest.mark.django_db
class TestGetExistingCompletionMetricIds:
    @pytest.fixture
    def setup_data(self):
        CompletionMetricFactory()
        completion_metrics = CompletionMetricFactory.create_batch(size=3)
        completion_metric_ids = [str(obj.id) for obj in completion_metrics]
        expected_response = completion_metric_ids.copy()
        completion_metric_ids += [str(uuid.uuid4())]

        return completion_metric_ids, expected_response

    def test_returns_existing_completion_metric_ids(self, setup_data):
        completion_metric_ids, expected_response = setup_data
        storage = ActivityGroupStorageImplementation()

        response = storage.get_existing_completion_metric_ids(
            completion_metric_ids)

        assert sorted(expected_response) == sorted(response)

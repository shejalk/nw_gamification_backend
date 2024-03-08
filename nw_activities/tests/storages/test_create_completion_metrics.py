import pytest

from nw_activities.models import CompletionMetric
from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import ActivityGroupConfigFactory
from nw_activities.tests.factories.storage_dtos import \
    CompletionMetricDTOFactory


@pytest.mark.django_db
class TestCreateCompletionMetrics:
    def test_creates_completion_metrics(self):
        activity_group_configs = ActivityGroupConfigFactory.create_batch(
            size=4)
        activity_group_ids = [str(obj.activity_group_id) for obj in
                              activity_group_configs]
        completion_metric_dtos = [
            CompletionMetricDTOFactory(
                activity_group_ids=activity_group_ids[:3]),
            CompletionMetricDTOFactory(
                activity_group_ids=activity_group_ids[3:]),
        ]
        storage = ActivityGroupStorageImplementation()

        storage.create_completion_metrics(completion_metric_dtos)

        completion_metric_id_wise_obj = {
            str(obj.id): obj
            for obj in CompletionMetric.objects.all()
        }
        for dto in completion_metric_dtos:
            obj = completion_metric_id_wise_obj[dto.id]
            assert dto.entity_id == str(obj.entity_id)
            assert dto.entity_type == obj.entity_type
            assert dto.value == obj.value
            activity_group_ids = obj.activitygroupconfig_set.all().values_list(
                "activity_group_id", flat=True)
            assert sorted(dto.activity_group_ids) == \
                   sorted(list(map(str, activity_group_ids)))

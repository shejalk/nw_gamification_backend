import uuid

import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import \
    ActivityGroupConfigFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupFrequencyConfigDTOFactory


@pytest.mark.django_db
class TestGetActivityGroupsFrequencyConfigs:
    @pytest.fixture
    def setup_data(self):
        activity_groups_frequency_configs = [
            ActivityGroupConfigFactory(),
            ActivityGroupConfigFactory(),
        ]
        ActivityGroupConfigFactory()

        activity_group_ids = [
            str(obj.activity_group_id)
            for obj in activity_groups_frequency_configs
        ]
        expected_response = [
            ActivityGroupFrequencyConfigDTOFactory(
                activity_group_id=activity_group_id)
            for activity_group_id in activity_group_ids
        ]
        activity_group_ids += [str(uuid.uuid4())]

        return activity_group_ids, expected_response

    def test_returns_activity_group_frequency_config_dtos(self, setup_data):
        activity_group_ids, expected_response = setup_data
        storage = ActivityGroupStorageImplementation()

        response = storage.get_activity_groups_frequency_configs(
            activity_group_ids)

        assert len(expected_response) == len(response)
        for dto in response:
            assert dto in expected_response

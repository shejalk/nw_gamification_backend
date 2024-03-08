import uuid

import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import RewardConfigFactory


@pytest.mark.django_db
class TestGetExistingRewardConfigIds:
    @pytest.fixture
    def setup_data(self):
        RewardConfigFactory()
        reward_configs = RewardConfigFactory.create_batch(size=3)
        reward_config_ids = [str(obj.id) for obj in reward_configs]
        expected_response = reward_config_ids.copy()
        reward_config_ids += [str(uuid.uuid4())]

        return reward_config_ids, expected_response

    def test_returns_existing_reward_config_ids(self, setup_data):
        reward_config_ids, expected_response = setup_data
        storage = ActivityGroupStorageImplementation()

        response = storage.get_existing_reward_config_ids(
            reward_config_ids)

        assert sorted(expected_response) == sorted(response)

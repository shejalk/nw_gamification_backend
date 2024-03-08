import uuid

import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import ActivityGroupConfigFactory, \
    RewardConfigFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupRewardConfigDTOFactory


@pytest.mark.django_db
class TestGetActivityGroupRewardConfigs:
    @pytest.fixture
    def setup_data(self):
        activity_groups = [
            ActivityGroupConfigFactory(),
            ActivityGroupConfigFactory(),
        ]
        ActivityGroupConfigFactory()
        reward_configs = [
            RewardConfigFactory(), RewardConfigFactory(),
            RewardConfigFactory(),
        ]
        activity_groups[0].reward_config.add(reward_configs[0],
                                             reward_configs[1])
        activity_groups[1].reward_config.add(reward_configs[2])
        activity_group_ids = [
            str(activity_group.activity_group_id)
            for activity_group in activity_groups
        ]
        expected_response = [
            ActivityGroupRewardConfigDTOFactory(
                id=str(reward_configs[0].id),
                activity_group_id=activity_group_ids[0],
                resource_reward_config_id=
                str(reward_configs[0].resource_reward_config_id),
            ),
            ActivityGroupRewardConfigDTOFactory(
                id=str(reward_configs[1].id),
                activity_group_id=activity_group_ids[0],
                resource_reward_config_id=
                str(reward_configs[1].resource_reward_config_id),
            ),
            ActivityGroupRewardConfigDTOFactory(
                id=str(reward_configs[2].id),
                activity_group_id=activity_group_ids[1],
                resource_reward_config_id=
                str(reward_configs[2].resource_reward_config_id),
            ),
        ]
        activity_group_ids += [str(uuid.uuid4())]

        return activity_group_ids, expected_response

    def test_returns_activity_group_reward_configs(self, setup_data):
        activity_group_ids, expected_response = setup_data
        storage = ActivityGroupStorageImplementation()

        response = storage.get_activity_group_reward_configs(
            activity_group_ids)

        assert len(expected_response) == len(response)
        for dto in response:
            assert dto in expected_response

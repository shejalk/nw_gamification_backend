import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import \
    UserActivityGroupInstanceRewardFactory, UserActivityGroupInstanceFactory, \
    RewardConfigFactory
from nw_activities.tests.factories.storage_dtos import \
    UserAGInstanceIdAGRewardConfigIdDTOFactory, \
    UserActivityGroupInstanceRewardDTOFactory


@pytest.mark.django_db
class TestGetLatestUserActivityGroupInstanceRewardsWithTransaction:
    @pytest.fixture
    def setup_data(self):
        user_activity_group_instances = \
            UserActivityGroupInstanceFactory.create_batch(size=2)
        activity_group_reward_configs = RewardConfigFactory.create_batch(
            size=2)
        user_ag_instance_rewards = [
            UserActivityGroupInstanceRewardFactory(
                user_activity_group_instance=user_activity_group_instances[0],
                activity_group_reward_config=activity_group_reward_configs[0],
            ),
            UserActivityGroupInstanceRewardFactory(
                user_activity_group_instance=user_activity_group_instances[1],
                activity_group_reward_config=activity_group_reward_configs[1],
            ),
            UserActivityGroupInstanceRewardFactory(
                user_activity_group_instance=user_activity_group_instances[0],
                activity_group_reward_config=activity_group_reward_configs[0],
            ),
            UserActivityGroupInstanceRewardFactory(
                user_activity_group_instance=user_activity_group_instances[1],
                activity_group_reward_config=activity_group_reward_configs[1],
            ),
        ]
        user_ag_instance_id_reward_config_id_dtos = [
            UserAGInstanceIdAGRewardConfigIdDTOFactory(
                user_activity_group_instance_id=
                str(user_activity_group_instances[0].id),
                activity_group_reward_config_id=
                str(activity_group_reward_configs[0].id),
            ),
            UserAGInstanceIdAGRewardConfigIdDTOFactory(
                user_activity_group_instance_id=
                str(user_activity_group_instances[1].id),
                activity_group_reward_config_id=
                str(activity_group_reward_configs[1].id),
            ),
        ]
        expected_response = [
            UserActivityGroupInstanceRewardDTOFactory(
                id=str(user_ag_instance_rewards[2].id),
                user_activity_group_instance_id=
                str(user_activity_group_instances[0].id),
                activity_group_reward_config_id=
                str(activity_group_reward_configs[0].id),
                rewarded_at_value=3.0,
            ),
            UserActivityGroupInstanceRewardDTOFactory(
                id=str(user_ag_instance_rewards[3].id),
                user_activity_group_instance_id=
                str(user_activity_group_instances[1].id),
                activity_group_reward_config_id=
                str(activity_group_reward_configs[1].id),
                rewarded_at_value=4.0,
            ),
        ]

        return user_ag_instance_id_reward_config_id_dtos, expected_response

    def test_returns_latest_user_activity_group_instance_rewards(
            self, setup_data):
        user_ag_instance_id_reward_config_id_dtos, expected_response = \
            setup_data
        storage = ActivityGroupStorageImplementation()

        response = storage.\
            get_latest_user_activity_group_instance_rewards_with_transaction(
                user_ag_instance_id_reward_config_id_dtos)

        assert len(response) == len(expected_response)
        for dto in response:
            assert dto in expected_response

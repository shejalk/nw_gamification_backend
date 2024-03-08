import pytest

from nw_activities.models import UserActivityGroupInstanceReward
from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import \
    UserActivityGroupInstanceFactory, RewardConfigFactory
from nw_activities.tests.factories.storage_dtos import \
    UserActivityGroupInstanceRewardDTOFactory


@pytest.mark.django_db
class TestCreateUserActivityGroupInstanceRewards:
    @pytest.fixture
    def setup_data(self):
        user_activity_group_instance_reward_dtos = [
            UserActivityGroupInstanceRewardDTOFactory(
                user_activity_group_instance_id
                =str(UserActivityGroupInstanceFactory().id),
                activity_group_reward_config_id=str(RewardConfigFactory().id),
            ),
            UserActivityGroupInstanceRewardDTOFactory(
                user_activity_group_instance_id
                =str(UserActivityGroupInstanceFactory().id),
                activity_group_reward_config_id=str(RewardConfigFactory().id),
            ),
        ]

        return user_activity_group_instance_reward_dtos

    def test_creates_user_activity_group_instance_rewards(self, setup_data):
        user_activity_group_instance_reward_dtos = setup_data
        storage = ActivityGroupStorageImplementation()

        storage.create_user_activity_group_instance_rewards(
            user_activity_group_instance_reward_dtos)

        user_activity_group_instance_id_wise_obj = {
            str(obj.id): obj
            for obj in UserActivityGroupInstanceReward.objects.all()
        }
        for dto in user_activity_group_instance_reward_dtos:
            obj = user_activity_group_instance_id_wise_obj[dto.id]
            assert dto.user_activity_group_instance_id == \
                   str(obj.user_activity_group_instance_id)
            assert dto.activity_group_reward_config_id == \
                   str(obj.activity_group_reward_config_id)
            assert dto.rewarded_at_value == obj.rewarded_at_value

import pytest

from nw_activities.models import RewardConfig
from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.storage_dtos import RewardConfigDTOFactory


@pytest.mark.django_db
class TestCreateRewardConfigs:
    def test_creates_reward_configs(self):
        reward_config_dtos = RewardConfigDTOFactory.create_batch(size=2)
        storage = ActivityGroupStorageImplementation()

        storage.create_reward_configs(reward_config_dtos)

        reward_config_id_wise_obj = {
            str(obj.id): obj
            for obj in RewardConfig.objects.all()
        }
        for dto in reward_config_dtos:
            obj = reward_config_id_wise_obj[dto.id]
            assert dto.resource_reward_config_id == \
                   obj.resource_reward_config_id

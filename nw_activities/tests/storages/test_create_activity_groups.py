import pytest

from nw_activities.models import ActivityGroup
from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import RewardConfigFactory
from nw_activities.tests.factories.storage_dtos import \
    CreateActivityGroupDTOFactory


@pytest.mark.django_db
class TestCreateActivityGroups:
    def test_creates_activity_groups(self):
        reward_configs = RewardConfigFactory.create_batch(size=4)
        create_activity_group_dtos = [
            CreateActivityGroupDTOFactory(
                reward_config_ids=[str(obj.id) for obj in reward_configs[:2]]),
            CreateActivityGroupDTOFactory(
                reward_config_ids=[str(obj.id) for obj in reward_configs[2:]]),
        ]
        storage = ActivityGroupStorageImplementation()

        storage.create_activity_groups(create_activity_group_dtos)

        activity_group_id_wise_obj = {
            str(obj.id): obj
            for obj in ActivityGroup.objects.all()
        }
        for dto in create_activity_group_dtos:
            obj = activity_group_id_wise_obj[dto.id]
            assert dto.name == obj.name
            assert dto.description == obj.description
            activity_group_config = obj.activitygroupconfig
            assert dto.frequency_type == \
                   activity_group_config.frequency_config.frequency_type
            assert dto.frequency_config == \
                   activity_group_config.frequency_config.config
            reward_config_ids = activity_group_config.reward_config.all()\
                .values_list("id", flat=True)
            assert sorted(dto.reward_config_ids) == \
                   sorted(list(map(str, reward_config_ids)))

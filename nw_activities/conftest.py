import pytest

from nw_activities.tests.factories.adapter_dtos import \
    UpdateUserResourceDTOFactory, UserResourceDTOFactory
from nw_activities.tests.factories.interactor_dtos import \
    UserActivityDTOFactory, UserInstanceTypeDTOFactory
from nw_activities.tests.factories.models import ActivityFactory, \
    ActivityGroupFactory, RewardConfigFactory, FrequencyConfigFactory, \
    ActivityGroupConfigFactory, UserActivityGroupInstanceFactory, \
    ActivityGroupAssociationFactory, CompletionMetricFactory, \
    UserActivityGroupInstanceMetricTrackerFactory, \
    UserActivityGroupInstanceRewardFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupAssociationDTOFactory, ActivityGroupFrequencyConfigDTOFactory, \
    UserActivityGroupInstanceDTOFactory, ActivityDTOFactory, \
    ActivityGroupInstanceIdentifierDTOFactory, \
    ActivityGroupCompletionMetricDTOFactory, \
    ActivityGroupInstanceCountDTOFactory, \
    UserActivityGroupInstanceMetricTrackerDTOFactory, \
    ActivityGroupRewardConfigDTOFactory, \
    UserActivityGroupInstanceRewardDTOFactory, CreateActivityGroupDTOFactory, \
    RewardConfigDTOFactory, CompletionMetricDTOFactory, \
    UserActivityGroupStreakDTOFactory, ActivityGroupOptionalMetricDTOFactory


@pytest.fixture(autouse=True)
def reset_model_factory_sequences():
    ActivityFactory.reset_sequence()
    ActivityGroupFactory.reset_sequence()
    RewardConfigFactory.reset_sequence()
    FrequencyConfigFactory.reset_sequence()
    FrequencyConfigFactory.frequency_type.reset()
    ActivityGroupConfigFactory.reset_sequence()
    UserActivityGroupInstanceFactory.reset_sequence()
    UserActivityGroupInstanceFactory.instance_type.reset()
    UserActivityGroupInstanceFactory.completion_status.reset()
    ActivityGroupAssociationFactory.reset_sequence()
    ActivityGroupAssociationFactory.association_type.reset()
    CompletionMetricFactory.reset_sequence()
    CompletionMetricFactory.entity_type.reset()
    UserActivityGroupInstanceMetricTrackerFactory.reset_sequence()
    UserActivityGroupInstanceRewardFactory.reset_sequence()


@pytest.fixture(autouse=True)
def reset_interactor_factory_sequences():
    UserActivityDTOFactory.reset_sequence()
    UserActivityDTOFactory.transaction_type.reset()
    UserInstanceTypeDTOFactory.instance_type.reset()


@pytest.fixture(autouse=True)
def reset_storage_factory_sequences():
    ActivityGroupAssociationDTOFactory.reset_sequence()
    ActivityGroupAssociationDTOFactory.association_type.reset()
    ActivityGroupFrequencyConfigDTOFactory.reset_sequence()
    ActivityGroupFrequencyConfigDTOFactory.frequency_type.reset()
    UserActivityGroupInstanceDTOFactory.reset_sequence()
    UserActivityGroupInstanceDTOFactory.completion_status.reset()
    ActivityDTOFactory.reset_sequence()
    ActivityGroupInstanceIdentifierDTOFactory.reset_sequence()
    ActivityGroupCompletionMetricDTOFactory.reset_sequence()
    ActivityGroupCompletionMetricDTOFactory.entity_type.reset()
    ActivityGroupInstanceCountDTOFactory.reset_sequence()
    UserActivityGroupInstanceMetricTrackerDTOFactory.reset_sequence()
    ActivityGroupRewardConfigDTOFactory.reset_sequence()
    UserActivityGroupInstanceRewardDTOFactory.reset_sequence()
    CreateActivityGroupDTOFactory.reset_sequence()
    CreateActivityGroupDTOFactory.frequency_type.reset()
    RewardConfigDTOFactory.reset_sequence()
    CompletionMetricDTOFactory.reset_sequence()
    CompletionMetricDTOFactory.entity_type.reset()
    UserActivityGroupStreakDTOFactory.reset_sequence()
    ActivityGroupOptionalMetricDTOFactory.reset_sequence()


@pytest.fixture(autouse=True)
def reset_adapter_factory_sequences():
    UpdateUserResourceDTOFactory.reset_sequence()
    UpdateUserResourceDTOFactory.transaction_type.reset()
    UserResourceDTOFactory.reset_sequence()

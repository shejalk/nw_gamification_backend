import datetime
import uuid

import factory

from nw_activities.constants.constants import \
    DATETIME_INSTANCE_IDENTIFIER_FORMAT
from nw_activities.constants.enum import FrequencyTypeEnum, InstanceTypeEnum, \
    CompletionStatusEnum, ActivityGroupAssociationTypeEnum, \
    CompletionMetricEntityTypeEnum, TransactionTypeEnum
from nw_activities.models import Activity, FrequencyConfig, \
    ActivityGroupConfig, ActivityGroup, RewardConfig, \
    UserActivityGroupInstance, ActivityGroupAssociation, CompletionMetric, \
    UserActivityGroupInstanceMetricTracker, UserActivityGroupInstanceReward, \
    UserActivityLog, UserActivityGroupStreak


class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Activity

    name_enum = factory.Sequence(lambda n: f"name_enum_{n+1}")
    name = factory.Sequence(lambda n: f"name_{n + 1}")
    description = factory.Sequence(lambda n: f"description_{n + 1}")


class ActivityGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActivityGroup

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    name = factory.Sequence(lambda n: f"name_{n + 1}")
    description = factory.Sequence(lambda n: f"description_{n + 1}")


class RewardConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RewardConfig

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    resource_reward_config_id = factory.Sequence(
        lambda n: f"resource_reward_config_id_{n + 1}")


class FrequencyConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FrequencyConfig

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    frequency_type = factory.Iterator(FrequencyTypeEnum.get_list_of_values())
    config = "{}"


class ActivityGroupConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActivityGroupConfig

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    activity_group = factory.SubFactory(ActivityGroupFactory)
    frequency_config = factory.SubFactory(FrequencyConfigFactory)


class UserActivityGroupInstanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserActivityGroupInstance

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def user_id(self):
        return str(uuid.uuid4())

    instance_identifier = factory.Sequence(
        lambda n: DATETIME_INSTANCE_IDENTIFIER_FORMAT.format(
            start_datetime_str=f"2022-08-{n+1} 09:00:00",
            end_datetime_str=f'2022-08-{n+1} 21:00:00'),
    )
    instance_type = factory.Iterator(InstanceTypeEnum.get_list_of_values())
    activity_group = factory.SubFactory(ActivityGroupFactory)
    completion_percentage = factory.Sequence(lambda n: n*0.5)
    completion_status = factory.Iterator(
        CompletionStatusEnum.get_list_of_values())


class ActivityGroupAssociationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActivityGroupAssociation

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def association_id(self):
        return str(uuid.uuid4())

    activity_group = factory.SubFactory(ActivityGroupFactory)
    association_type = factory.Iterator(
        ActivityGroupAssociationTypeEnum.get_list_of_values())


class CompletionMetricFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CompletionMetric

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    entity_id = factory.Sequence(lambda n: f"entity_id_{n + 1}")
    entity_type = factory.Iterator(
        CompletionMetricEntityTypeEnum.get_list_of_values())
    value = factory.Sequence(lambda n: n + 1.0)


class UserActivityGroupInstanceMetricTrackerFactory(
        factory.django.DjangoModelFactory):
    class Meta:
        model = UserActivityGroupInstanceMetricTracker

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    user_activity_group_instance = factory.SubFactory(
        UserActivityGroupInstanceFactory)
    activity_group_completion_metric = factory.SubFactory(
        CompletionMetricFactory)
    current_value = factory.Sequence(lambda n: n + 1.0)


class UserActivityGroupInstanceRewardFactory(
        factory.django.DjangoModelFactory):
    class Meta:
        model = UserActivityGroupInstanceReward

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    user_activity_group_instance = factory.SubFactory(
        UserActivityGroupInstanceFactory)
    activity_group_reward_config = factory.SubFactory(RewardConfigFactory)
    rewarded_at_value = factory.Sequence(lambda n: n + 1.0)


class UserActivityLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserActivityLog

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def user_id(self):
        return str(uuid.uuid4())

    activity = factory.SubFactory(ActivityFactory)
    entity_id = factory.Sequence(lambda n: f"entity_id_{n + 1}")
    entity_type = factory.Sequence(lambda n: f"entity_type_{n + 1}")
    resource_name_enum = factory.Sequence(
        lambda n: f"resource_name_enum_{n + 1}")
    resource_value = factory.Sequence(lambda n: n + 1.0)
    transaction_type = TransactionTypeEnum.CREDIT.value


class UserActivityGroupStreakFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserActivityGroupStreak

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def user_id(self):
        return str(uuid.uuid4())

    activity_group = factory.SubFactory(ActivityGroupFactory)
    current_streak_count = factory.Sequence(lambda n: n + 1)
    max_streak_count = factory.Sequence(lambda n: n + 1.0)
    last_updated_at = datetime.datetime.now()

import uuid
from datetime import datetime

import factory

from nw_activities.constants.enum import ActivityGroupAssociationTypeEnum, \
    FrequencyTypeEnum, CompletionStatusEnum, InstanceTypeEnum, \
    CompletionMetricEntityTypeEnum, OptionalMetricEntityTypeEnum
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import ActivityGroupAssociationDTO, \
    ActivityGroupFrequencyConfigDTO, UserActivityGroupInstanceDTO, \
    ActivityGroupInstanceIdentifierDTO, ActivityGroupCompletionMetricDTO, \
    ActivityGroupInstanceCountDTO, UserActivityGroupInstanceMetricTrackerDTO, \
    ActivityGroupRewardConfigDTO, UserActivityGroupInstanceRewardDTO, \
    CreateActivityGroupDTO, RewardConfigDTO, CompletionMetricDTO, \
    UserAGInstanceIdAGRewardConfigIdDTO, ActivityGroupOptionalMetricDTO, \
    UserActivityGroupStreakDTO, UserActivityGroupInstanceWithDatetimeDTO
from nw_activities.interactors.storage_interfaces.activity_storage_interface \
    import ActivityDTO


class ActivityGroupAssociationDTOFactory(factory.Factory):
    class Meta:
        model = ActivityGroupAssociationDTO

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def activity_group_id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def association_id(self):
        return str(uuid.uuid4())

    association_type = factory.Iterator(
        ActivityGroupAssociationTypeEnum.get_list_of_values())


class ActivityGroupFrequencyConfigDTOFactory(factory.Factory):
    class Meta:
        model = ActivityGroupFrequencyConfigDTO

    @factory.lazy_attribute
    def activity_group_id(self):
        return str(uuid.uuid4())

    frequency_type = factory.Iterator(FrequencyTypeEnum.get_list_of_values())
    config = {}


class UserActivityGroupInstanceDTOFactory(factory.Factory):
    class Meta:
        model = UserActivityGroupInstanceDTO

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def user_id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def activity_group_id(self):
        return str(uuid.uuid4())

    instance_identifier = factory.Sequence(lambda n: f"identifier_{n + 1}")
    completion_percentage = factory.Sequence(lambda n: n + 1.0)
    completion_status = factory.Iterator(
        CompletionStatusEnum.get_list_of_values())
    instance_type = InstanceTypeEnum.DEFAULT.value


class ActivityDTOFactory(factory.Factory):
    class Meta:
        model = ActivityDTO

    name_enum = factory.Sequence(lambda n: f"name_enum_{n + 1}")
    name = factory.Sequence(lambda n: f"name_{n + 1}")
    description = factory.Sequence(lambda n: f"description_{n + 1}")


class ActivityGroupInstanceIdentifierDTOFactory(factory.Factory):
    class Meta:
        model = ActivityGroupInstanceIdentifierDTO

    @factory.lazy_attribute
    def activity_group_id(self):
        return str(uuid.uuid4())

    instance_identifier = factory.Sequence(lambda n: f"identifier_{n + 1}")


class ActivityGroupCompletionMetricDTOFactory(factory.Factory):
    class Meta:
        model = ActivityGroupCompletionMetricDTO

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def entity_id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def activity_group_id(self):
        return str(uuid.uuid4())

    entity_type = factory.Iterator(
        CompletionMetricEntityTypeEnum.get_list_of_values())
    value = factory.Sequence(lambda n: n + 1)


class ActivityGroupInstanceCountDTOFactory(factory.Factory):
    class Meta:
        model = ActivityGroupInstanceCountDTO

    @factory.lazy_attribute
    def activity_group_id(self):
        return str(uuid.uuid4())

    activity_group_instances_count = factory.Sequence(lambda n: n + 1)


class UserActivityGroupInstanceMetricTrackerDTOFactory(factory.Factory):
    class Meta:
        model = UserActivityGroupInstanceMetricTrackerDTO

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def user_activity_group_instance_id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def activity_group_completion_metric_id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def activity_group_optional_metric_id(self):
        return None

    current_value = factory.Sequence(lambda n: n + 1)


class ActivityGroupRewardConfigDTOFactory(factory.Factory):
    class Meta:
        model = ActivityGroupRewardConfigDTO

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def activity_group_id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def resource_reward_config_id(self):
        return str(uuid.uuid4())


class UserActivityGroupInstanceRewardDTOFactory(factory.Factory):
    class Meta:
        model = UserActivityGroupInstanceRewardDTO

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def user_activity_group_instance_id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def activity_group_reward_config_id(self):
        return str(uuid.uuid4())

    rewarded_at_value = factory.Sequence(lambda n: n + 1.0)


class CreateActivityGroupDTOFactory(factory.Factory):
    class Meta:
        model = CreateActivityGroupDTO

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    name = factory.Sequence(lambda n: f"name_{n + 1}")
    description = factory.Sequence(lambda n: f"description_{n + 1}")
    frequency_type = factory.Iterator(FrequencyTypeEnum.get_list_of_values())
    frequency_config = "{}"
    reward_config_ids = []


class RewardConfigDTOFactory(factory.Factory):
    class Meta:
        model = RewardConfigDTO

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def resource_reward_config_id(self):
        return str(uuid.uuid4())


class CompletionMetricDTOFactory(factory.Factory):
    class Meta:
        model = CompletionMetricDTO

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def entity_id(self):
        return str(uuid.uuid4())

    entity_type = factory.Iterator(
        CompletionMetricEntityTypeEnum.get_list_of_values())
    value = factory.Sequence(lambda n: n + 1.0)
    activity_group_ids = []


class UserAGInstanceIdAGRewardConfigIdDTOFactory(factory.Factory):
    class Meta:
        model = UserAGInstanceIdAGRewardConfigIdDTO

    @factory.lazy_attribute
    def user_activity_group_instance_id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def activity_group_reward_config_id(self):
        return str(uuid.uuid4())


class ActivityGroupOptionalMetricDTOFactory(factory.Factory):
    class Meta:
        model = ActivityGroupOptionalMetricDTO

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def activity_group_id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def entity_id(self):
        return str(uuid.uuid4())

    entity_type = factory.Iterator(
        OptionalMetricEntityTypeEnum.get_list_of_values())


class UserActivityGroupStreakDTOFactory(factory.Factory):
    class Meta:
        model = UserActivityGroupStreakDTO

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def user_id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def activity_group_id(self):
        return str(uuid.uuid4())

    streak_count = factory.Sequence(lambda n: n + 1)
    max_streak_count = factory.Sequence(lambda n: n + 1)
    last_updated_at = datetime.now()


class UserActivityGroupInstanceWithDatetimeDTOFactory(factory.Factory):
    class Meta:
        model = UserActivityGroupInstanceWithDatetimeDTO

    @factory.lazy_attribute
    def id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def user_id(self):
        return str(uuid.uuid4())

    @factory.lazy_attribute
    def activity_group_id(self):
        return str(uuid.uuid4())

    instance_identifier = factory.Sequence(lambda n: f"identifier_{n + 1}")
    completion_percentage = factory.Sequence(lambda n: n + 1.0)
    completion_status = factory.Iterator(
        CompletionStatusEnum.get_list_of_values())
    instance_type = InstanceTypeEnum.DEFAULT.value
    start_datetime = datetime(2023, 12, 25, 5, 30)
    end_datetime = datetime(2023, 12, 27, 5, 30)

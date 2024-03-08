import datetime
import uuid

import factory

from nw_activities.constants.enum import FrequencyTypeEnum, \
    CompletionStatusEnum, InstanceTypeEnum, CompletionMetricEntityTypeEnum, \
    TransactionTypeEnum
from nw_activities.interactors.dtos import \
    UserActivityGroupInstanceWithAssociationDTO, ActivityGroupInstanceDTO, \
    UserCompletionMetricDTO, UserActivityGroupCompletionMetricDTO, \
    UserActivityDTO, UserInstanceTypeDTO


class ActivityGroupInstanceDTOFactory(factory.Factory):
    class Meta:
        model = ActivityGroupInstanceDTO

    instance_identifier = factory.Sequence(lambda n: f"identifier_{n + 1}")

    @factory.lazy_attribute
    def activity_group_id(self):
        return str(uuid.uuid4())

    completion_percentage = factory.Sequence(lambda n: n + 1.0)
    completion_status = factory.Iterator(
        CompletionStatusEnum.get_list_of_values())
    start_datetime = datetime.datetime.now()
    end_datetime = datetime.datetime.now()
    instance_type = InstanceTypeEnum.DEFAULT.value


class UserActivityGroupInstanceWithAssociationDTOFactory(factory.Factory):
    class Meta:
        model = UserActivityGroupInstanceWithAssociationDTO

    @factory.lazy_attribute
    def user_id(self):
        return str(uuid.uuid4())

    frequency_type = factory.Iterator(FrequencyTypeEnum.get_list_of_values())
    activity_group_instance = factory.SubFactory(
        ActivityGroupInstanceDTOFactory)
    association_activity_group_instances = factory.List(
        factory.SubFactory(ActivityGroupInstanceDTOFactory)
        for _ in range(2)
    )


class UserCompletionMetricDTOFactory(factory.Factory):
    class Meta:
        model = UserCompletionMetricDTO

    target_value = factory.Sequence(lambda n: n + 1)
    current_value = factory.Sequence(lambda n: n + 1)

    @factory.lazy_attribute
    def entity_id(self):
        return str(uuid.uuid4())

    entity_type = factory.Iterator(
        CompletionMetricEntityTypeEnum.get_list_of_values())


class UserActivityGroupCompletionMetricDTOFactory(factory.Factory):
    class Meta:
        model = UserActivityGroupCompletionMetricDTO

    @factory.lazy_attribute
    def activity_group_id(self):
        return str(uuid.uuid4())

    instance_completion_metrics = factory.List(
        factory.SubFactory(UserCompletionMetricDTOFactory)
        for _ in range(2)
    )

    no_of_activity_group_instances_completed = factory.Sequence(
        lambda n: n + 1)


class UserActivityDTOFactory(factory.Factory):
    class Meta:
        model = UserActivityDTO

    @factory.lazy_attribute
    def user_id(self):
        return str(uuid.uuid4())

    activity_name_enum = factory.Sequence(
        lambda n: f"activity_name_enum_{n + 1}")
    entity_id = factory.Sequence(lambda n: f"entity_id_{n + 1}")
    entity_type = factory.Sequence(lambda n: f"entity_type_{n + 1}")
    resource_name_enum = factory.Sequence(
        lambda n: f"resource_name_enum_{n + 1}")
    resource_value = factory.Sequence(lambda n: n + 1.0)
    transaction_type = factory.Iterator(
        TransactionTypeEnum.get_list_of_values())


class UserInstanceTypeDTOFactory(factory.Factory):
    class Meta:
        model = UserInstanceTypeDTO

    @factory.lazy_attribute
    def user_id(self):
        return str(uuid.uuid4())

    instance_type = factory.Iterator(InstanceTypeEnum.get_list_of_values())

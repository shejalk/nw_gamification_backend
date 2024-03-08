import datetime
from dataclasses import dataclass
from typing import List

from nw_activities.constants.enum import TransactionTypeEnum, \
    CompletionStatusEnum, FrequencyTypeEnum, \
    CompletionMetricEntityTypeEnum, RewardTypeEnum, InstanceTypeEnum, \
    OptionalMetricEntityTypeEnum


@dataclass
class UserActivityDTO:
    user_id: str
    activity_name_enum: str
    entity_id: str
    entity_type: str
    resource_name_enum: str
    resource_value: float
    transaction_type: TransactionTypeEnum


@dataclass
class ActivityGroupInstanceDTO:
    instance_identifier: str
    instance_type: InstanceTypeEnum
    activity_group_id: str
    completion_percentage: float
    completion_status: CompletionStatusEnum
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime


@dataclass
class UserActivityGroupInstanceWithAssociationDTO:
    user_id: str
    frequency_type: FrequencyTypeEnum
    activity_group_instance: ActivityGroupInstanceDTO
    association_activity_group_instances: List[ActivityGroupInstanceDTO]


@dataclass
class UserCompletionMetricDTO:
    target_value: float
    current_value: float
    entity_id: str
    entity_type: CompletionMetricEntityTypeEnum


@dataclass
class UserActivityGroupCompletionMetricDTO:
    activity_group_id: str
    instance_completion_metrics: List[UserCompletionMetricDTO]
    no_of_activity_group_instances_completed: int


@dataclass
class RewardResourceDetailsDTO:
    resource_value: float
    resource_type: str


@dataclass
class UserActivityGroupRewardDetailsDTO:
    activity_group_id: str
    reward_type: RewardTypeEnum
    resource_details: RewardResourceDetailsDTO
    is_earned: bool


@dataclass
class ActivityGroupIdRewardTypeDTO:
    activity_group_id: str
    reward_type: RewardTypeEnum


@dataclass
class UserInstanceTypeDTO:
    user_id: str
    instance_type: InstanceTypeEnum


@dataclass
class UserOptionalMetricDTO:
    current_value: float
    entity_id: str
    entity_type: OptionalMetricEntityTypeEnum


@dataclass
class UserActivityGroupMetricsDTO:
    user_id: str
    instance_id: str
    instance_identifier: str
    instance_type: InstanceTypeEnum
    activity_group_id: str
    completion_percentage: float
    completion_status: CompletionStatusEnum
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    instance_completion_metrics: List[UserCompletionMetricDTO]
    instance_optional_metrics: List[UserOptionalMetricDTO]

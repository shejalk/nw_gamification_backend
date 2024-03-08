import abc
import datetime
from dataclasses import dataclass
from typing import List, Optional, Any, Dict

from nw_activities.constants.enum import ActivityGroupAssociationTypeEnum, \
    CompletionStatusEnum, CompletionMetricEntityTypeEnum, \
    FrequencyTypeEnum, InstanceTypeEnum, OptionalMetricEntityTypeEnum


@dataclass
class UserActivityGroupInstanceDTO:
    id: str
    user_id: str
    instance_identifier: str
    instance_type: InstanceTypeEnum
    activity_group_id: str
    completion_percentage: float
    completion_status: CompletionStatusEnum


@dataclass
class ActivityGroupCompletionMetricDTO:
    id: str
    activity_group_id: str
    entity_id: str
    entity_type: CompletionMetricEntityTypeEnum
    value: Any


@dataclass
class ActivityGroupFrequencyConfigDTO:
    activity_group_id: str
    frequency_type: FrequencyTypeEnum
    config: Dict[str, Any]


@dataclass
class ActivityGroupInstanceIdentifierDTO:
    activity_group_id: str
    instance_identifier: str


@dataclass
class ActivityGroupAssociationDTO:
    id: str
    activity_group_id: str
    association_id: str
    association_type: ActivityGroupAssociationTypeEnum


@dataclass
class UserActivityGroupInstanceMetricTrackerDTO:
    id: str
    user_activity_group_instance_id: str
    activity_group_completion_metric_id: Optional[str]
    activity_group_optional_metric_id: Optional[str]
    current_value: float


@dataclass
class ActivityGroupRewardConfigDTO:
    id: str
    activity_group_id: str
    resource_reward_config_id: str


@dataclass
class UserActivityGroupInstanceRewardDTO:
    id: str
    user_activity_group_instance_id: str
    activity_group_reward_config_id: str
    rewarded_at_value: float


@dataclass
class ActivityGroupInstanceCountDTO:
    activity_group_id: str
    activity_group_instances_count: float


@dataclass
class UserAGInstanceIdAGRewardConfigIdDTO:
    user_activity_group_instance_id: str
    activity_group_reward_config_id: str


@dataclass
class CreateActivityGroupDTO:
    id: str
    name: str
    description: Optional[str]
    frequency_type: FrequencyTypeEnum
    frequency_config: str
    reward_config_ids: List[str]


@dataclass
class RewardConfigDTO:
    id: str
    resource_reward_config_id: str


@dataclass
class CompletionMetricDTO:
    id: str
    entity_id: str
    entity_type: CompletionMetricEntityTypeEnum
    value: Any
    activity_group_ids: List[str]


@dataclass
class ActivityGroupOptionalMetricDTO:
    id: str
    activity_group_id: str
    entity_id: str
    entity_type: OptionalMetricEntityTypeEnum


@dataclass
class UserActivityGroupStreakDTO:
    id: str
    user_id: str
    activity_group_id: str
    streak_count: int
    max_streak_count: int
    last_updated_at: datetime.datetime


@dataclass
class UserActivityGroupInstanceWithDatetimeDTO(UserActivityGroupInstanceDTO):
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime


class ActivityGroupStorageInterface(abc.ABC):

    @abc.abstractmethod
    def get_activity_group_associations_for_association_ids(
            self, association_ids: List[str]) -> \
            List[ActivityGroupAssociationDTO]:
        pass

    @abc.abstractmethod
    def get_activity_groups_frequency_configs(
            self, activity_group_ids: List[str]) -> \
            List[ActivityGroupFrequencyConfigDTO]:
        pass

    @abc.abstractmethod
    def get_activity_groups_completion_metrics(
            self, activity_group_ids: List[str]) -> \
            List[ActivityGroupCompletionMetricDTO]:
        pass

    @abc.abstractmethod
    def get_user_activity_group_instances(
            self, user_id: str,
            activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO],
    ) -> List[UserActivityGroupInstanceDTO]:
        pass

    @abc.abstractmethod
    def get_user_activity_group_instances_metric_tracker(
            self, user_activity_group_instance_ids: List[str],
    ) -> List[UserActivityGroupInstanceMetricTrackerDTO]:
        pass

    @abc.abstractmethod
    def get_user_activity_group_instances_metric_tracker_without_transaction(
            self, user_activity_group_instance_ids: List[str]) -> \
            List[UserActivityGroupInstanceMetricTrackerDTO]:
        pass

    @abc.abstractmethod
    def create_user_activity_group_instances(
            self, user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO]):
        pass

    @abc.abstractmethod
    def update_user_activity_group_instances(
            self, user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO]):
        pass

    @abc.abstractmethod
    def get_activity_group_associations_for_activity_group_ids(
            self, activity_group_ids: List[str]) -> \
            List[ActivityGroupAssociationDTO]:
        pass

    @abc.abstractmethod
    def create_user_activity_group_instances_metric_tracker(
            self, user_activity_group_instance_metric_dtos:
            List[UserActivityGroupInstanceMetricTrackerDTO]):
        pass

    @abc.abstractmethod
    def update_user_activity_group_instances_metric_tracker(
            self, user_activity_group_instance_metric_dtos:
            List[UserActivityGroupInstanceMetricTrackerDTO]):
        pass

    @abc.abstractmethod
    def get_all_activity_group_ids(self) -> List[str]:
        pass

    @abc.abstractmethod
    def get_activity_group_reward_configs(
            self, activity_group_ids: List[str]) -> \
            List[ActivityGroupRewardConfigDTO]:
        pass

    @abc.abstractmethod
    def get_latest_user_activity_group_instance_rewards(
            self, user_ag_instance_id_reward_config_id_dtos:
            List[UserAGInstanceIdAGRewardConfigIdDTO],
    ) -> List[UserActivityGroupInstanceRewardDTO]:
        pass

    @abc.abstractmethod
    def get_latest_user_activity_group_instance_rewards_with_transaction(
            self, user_ag_instance_id_reward_config_id_dtos:
            List[UserAGInstanceIdAGRewardConfigIdDTO],
    ) -> List[UserActivityGroupInstanceRewardDTO]:
        pass

    @abc.abstractmethod
    def create_user_activity_group_instance_rewards(
            self, user_activity_group_instance_reward_dtos:
            List[UserActivityGroupInstanceRewardDTO]):
        pass

    @abc.abstractmethod
    def get_activity_group_associations(
            self, activity_group_association_ids: List[str]) -> \
            List[ActivityGroupAssociationDTO]:
        pass

    @abc.abstractmethod
    def get_activity_group_instances_count_for_completion_status(
            self, user_id: str, activity_group_ids: List[str],
            completion_status: CompletionStatusEnum,
    ) -> List[ActivityGroupInstanceCountDTO]:
        pass

    @abc.abstractmethod
    def get_existing_activity_group_ids(self, activity_group_ids: List[str]) \
            -> List[str]:
        pass

    @abc.abstractmethod
    def create_activity_group_associations(
            self, activity_group_association_dtos:
            List[ActivityGroupAssociationDTO]):
        pass

    @abc.abstractmethod
    def get_existing_completion_metric_ids(
            self, completion_metric_ids: List[str]) -> List[str]:
        pass

    @abc.abstractmethod
    def get_existing_reward_config_ids(
            self, reward_config_ids: List[str]) -> List[str]:
        pass

    @abc.abstractmethod
    def create_activity_groups(
            self, activity_group_dtos: List[CreateActivityGroupDTO]):
        pass

    @abc.abstractmethod
    def create_reward_configs(
            self, reward_config_dtos: List[RewardConfigDTO]):
        pass

    @abc.abstractmethod
    def create_completion_metrics(
            self, completion_metric_dtos: List[CompletionMetricDTO]):
        pass

    @abc.abstractmethod
    def get_existing_activity_group_association_ids(
            self, activity_group_association_entity_ids: List[str]) -> \
            List[str]:
        pass

    @abc.abstractmethod
    def get_all_users_activity_group_instances(
            self, activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO],
    ) -> List[UserActivityGroupInstanceDTO]:
        pass

    @abc.abstractmethod
    def get_activity_group_instance_user_ids_for_instance_type(
            self, activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO],
            instance_type: InstanceTypeEnum) -> List[str]:
        pass

    @abc.abstractmethod
    def get_activity_groups_optional_metrics(
            self, activity_group_ids: List[str]) -> \
            List[ActivityGroupOptionalMetricDTO]:
        pass

    @abc.abstractmethod
    def get_streak_enabled_activity_group_ids(self) -> List[str]:
        pass

    @abc.abstractmethod
    def get_user_activity_group_streak_details(self, user_id: str):
        pass

    @abc.abstractmethod
    def get_user_activity_group_streaks(
            self, user_id: str, activity_group_ids: List[str],
    ) -> List[UserActivityGroupStreakDTO]:
        pass

    @abc.abstractmethod
    def create_user_activity_groups_streak(
            self, user_activity_group_streak_dtos:
            List[UserActivityGroupStreakDTO]):
        pass

    @abc.abstractmethod
    def update_user_activity_groups_streak(
            self, user_activity_group_streak_dtos:
            List[UserActivityGroupStreakDTO]):
        pass

    @abc.abstractmethod
    def get_activity_group_instance_user_ids_for_instance_types(
            self, activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO],
            instance_types: List[InstanceTypeEnum], user_ids: List[str],
    ) -> List[str]:
        pass

    @abc.abstractmethod
    def get_users_activity_group_instances(
            self, user_ids: List[str], activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO],
    ) -> List[UserActivityGroupInstanceDTO]:
        pass

    @abc.abstractmethod
    def delete_user_activity_group_instances(
            self, user_activity_group_instance_ids: List[str]):
        pass

    @abc.abstractmethod
    def get_user_activity_group_streak_details_with_transaction(
            self, user_id: str) -> List[UserActivityGroupStreakDTO]:
        pass

    @abc.abstractmethod
    def get_max_streak_for_user_ids(self, user_ids: List[str]) -> int:
        pass

    @abc.abstractmethod
    def update_user_activity_group_streak_last_updated_at(
            self, user_id: str, last_updated_at: datetime.datetime):
        pass

    @abc.abstractmethod
    def get_user_activity_group_streaks_up_to_max_rank(
            self, user_ids: List[str], activity_group_ids: List[str],
            max_rank: int) -> List[UserActivityGroupStreakDTO]:
        pass

    @abc.abstractmethod
    def get_user_activity_group_streak_for_given_streak(
            self, activity_group_ids: List[str], streak: int) -> \
            List[UserActivityGroupStreakDTO]:
        pass

    @abc.abstractmethod
    def get_user_activity_group_streaks_for_user_ids(
            self, user_ids: List[str], activity_group_ids: List[str],
    ) -> List[UserActivityGroupStreakDTO]:
        pass

    @abc.abstractmethod
    def get_user_activity_group_instances_of_given_types(
            self, user_id: str, activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO],
            instance_types: List[InstanceTypeEnum],
    ) -> List[UserActivityGroupInstanceDTO]:
        pass

    def get_agi_user_ids_for_instance_types_completion_types(
            self, activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO],
            instance_types: List[InstanceTypeEnum], user_ids: List[str],
            completion_types: List[CompletionStatusEnum]
    ) -> List[str]:
        pass

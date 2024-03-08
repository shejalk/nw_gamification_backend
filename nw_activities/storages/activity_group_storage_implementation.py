import datetime
import json
from collections import defaultdict
from typing import List

from django.db.models import OuterRef, Subquery, Count, Q, Max
from ib_common.date_time_utils.get_current_local_date_time import \
    get_current_local_date_time

from nw_activities.constants.enum import CompletionStatusEnum, InstanceTypeEnum
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import \
    ActivityGroupStorageInterface, UserActivityGroupInstanceMetricTrackerDTO, \
    ActivityGroupAssociationDTO, UserActivityGroupInstanceDTO, \
    ActivityGroupInstanceIdentifierDTO, ActivityGroupCompletionMetricDTO, \
    ActivityGroupFrequencyConfigDTO, ActivityGroupInstanceCountDTO, \
    UserActivityGroupInstanceRewardDTO, ActivityGroupRewardConfigDTO, \
    UserAGInstanceIdAGRewardConfigIdDTO, CompletionMetricDTO, \
    RewardConfigDTO, CreateActivityGroupDTO, ActivityGroupOptionalMetricDTO, \
    UserActivityGroupStreakDTO
from nw_activities.models import ActivityGroupAssociation, \
    ActivityGroup, ActivityGroupConfig, CompletionMetric, RewardConfig, \
    FrequencyConfig, UserActivityGroupInstanceReward, \
    UserActivityGroupInstance, UserActivityGroupInstanceMetricTracker, \
    UserActivityGroupStreak


class ActivityGroupStorageImplementation(ActivityGroupStorageInterface):

    def get_activity_group_reward_configs(
            self, activity_group_ids: List[str]) -> \
            List[ActivityGroupRewardConfigDTO]:
        activity_group_configs = ActivityGroupConfig.objects.filter(
            activity_group_id__in=activity_group_ids).prefetch_related(
            'reward_config')
        activity_group_reward_configs = []
        for each in activity_group_configs:
            if each.reward_config:
                reward_configs = each.reward_config.all()
                for reward_config in reward_configs:
                    activity_group_reward_configs.append(
                        ActivityGroupRewardConfigDTO(
                            id=str(reward_config.id),
                            activity_group_id=str(each.activity_group_id),
                            resource_reward_config_id=
                            reward_config.resource_reward_config_id,
                        ),
                    )
        return activity_group_reward_configs

    def get_latest_user_activity_group_instance_rewards(
            self, user_ag_instance_id_reward_config_id_dtos:
            List[UserAGInstanceIdAGRewardConfigIdDTO],
    ) -> List[UserActivityGroupInstanceRewardDTO]:
        if not user_ag_instance_id_reward_config_id_dtos:
            return []

        latest_user_activity_group_instance_reward_ids = \
            self._latest_user_activity_group_instance_reward_ids(
                user_ag_instance_id_reward_config_id_dtos)

        latest_user_activity_group_instance_rewards = \
            UserActivityGroupInstanceReward.objects.filter(
                id__in=latest_user_activity_group_instance_reward_ids)

        user_activity_group_instance_reward_dtos = \
            self._convert_user_activity_group_instance_reward_objs_into_dtos(
                latest_user_activity_group_instance_rewards)

        return user_activity_group_instance_reward_dtos

    def get_latest_user_activity_group_instance_rewards_with_transaction(
            self, user_ag_instance_id_reward_config_id_dtos:
            List[UserAGInstanceIdAGRewardConfigIdDTO],
    ) -> List[UserActivityGroupInstanceRewardDTO]:
        if not user_ag_instance_id_reward_config_id_dtos:
            return []

        latest_user_activity_group_instance_reward_ids = \
            self._latest_user_activity_group_instance_reward_ids(
                user_ag_instance_id_reward_config_id_dtos)

        latest_user_activity_group_instance_rewards = \
            UserActivityGroupInstanceReward.objects.select_for_update().filter(
                id__in=latest_user_activity_group_instance_reward_ids)

        user_activity_group_instance_reward_dtos = \
            self._convert_user_activity_group_instance_reward_objs_into_dtos(
                latest_user_activity_group_instance_rewards)

        return user_activity_group_instance_reward_dtos

    def create_user_activity_group_instance_rewards(
            self, user_activity_group_instance_reward_dtos:
            List[UserActivityGroupInstanceRewardDTO]):
        user_activity_group_instance_rewards = [
            UserActivityGroupInstanceReward(
                id=dto.id,
                user_activity_group_instance_id=
                dto.user_activity_group_instance_id,
                activity_group_reward_config_id=
                dto.activity_group_reward_config_id,
                rewarded_at_value=dto.rewarded_at_value,
            )
            for dto in user_activity_group_instance_reward_dtos
        ]
        UserActivityGroupInstanceReward.objects.bulk_create(
            user_activity_group_instance_rewards)

    def get_activity_group_associations(
            self, activity_group_association_ids: List[str]) -> \
            List[ActivityGroupAssociationDTO]:
        activity_group_associations = ActivityGroupAssociation.objects.filter(
            id__in=activity_group_association_ids)
        activity_group_association_dtos = [
            self._convert_activity_group_association_to_dto(each)
            for each in activity_group_associations
        ]
        return activity_group_association_dtos

    def get_activity_group_instances_count_for_completion_status(
            self, user_id: str, activity_group_ids: List[str],
            completion_status: CompletionStatusEnum,
    ) -> List[ActivityGroupInstanceCountDTO]:
        user_activity_group_instances = \
            UserActivityGroupInstance.objects.filter(
                user_id=user_id, activity_group_id__in=activity_group_ids,
                completion_status=completion_status,
            ).values('activity_group_id').annotate(instances_count=Count('id'))

        activity_group_instances_count_dtos = [
            ActivityGroupInstanceCountDTO(
                activity_group_id=str(each['activity_group_id']),
                activity_group_instances_count=each['instances_count'],
            )
            for each in user_activity_group_instances
        ]

        return activity_group_instances_count_dtos

    def get_activity_group_associations_for_association_ids(
            self, association_ids: List[str]) -> \
            List[ActivityGroupAssociationDTO]:
        activity_group_associations = ActivityGroupAssociation.objects.filter(
            association_id__in=association_ids)
        activity_group_association_dtos = [
            self._convert_activity_group_association_to_dto(each)
            for each in activity_group_associations
        ]
        return activity_group_association_dtos

    def get_activity_groups_frequency_configs(
            self, activity_group_ids: List[str]) -> \
            List[ActivityGroupFrequencyConfigDTO]:
        activity_group_configs = ActivityGroupConfig.objects.filter(
            activity_group_id__in=activity_group_ids).select_related(
            'frequency_config')
        activity_group_frequency_config_dtos = [
            ActivityGroupFrequencyConfigDTO(
                activity_group_id=str(each.activity_group_id),
                frequency_type=each.frequency_config.frequency_type,
                config=json.loads(each.frequency_config.config),
            )
            for each in activity_group_configs
        ]
        return activity_group_frequency_config_dtos

    def get_activity_groups_completion_metrics(
            self, activity_group_ids: List[str]) -> \
            List[ActivityGroupCompletionMetricDTO]:
        activity_group_configs = ActivityGroupConfig.objects.filter(
            activity_group_id__in=activity_group_ids).prefetch_related(
            'completion_metric')
        activity_group_completion_metrics = []
        for each in activity_group_configs:
            if each.completion_metric:
                completion_metrics = each.completion_metric.all()
                for completion_metric in completion_metrics:
                    activity_group_completion_metrics.append(
                        ActivityGroupCompletionMetricDTO(
                            id=str(completion_metric.id),
                            activity_group_id=str(each.activity_group_id),
                            entity_id=completion_metric.entity_id,
                            entity_type=completion_metric.entity_type,
                            value=round(completion_metric.value, 2),
                        ),
                    )
        return activity_group_completion_metrics

    def get_user_activity_group_instances(
            self, user_id: str, activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO],
    ) -> List[UserActivityGroupInstanceDTO]:
        filter_objects = None
        for dto in activity_group_instance_identifier_dtos:
            q_object = Q(activity_group_id=dto.activity_group_id,
                         instance_identifier=dto.instance_identifier)
            if filter_objects is None:
                filter_objects = q_object
            else:
                filter_objects |= q_object

        if not filter_objects:
            return []

        user_activity_group_instances = \
            UserActivityGroupInstance.objects.filter(
                filter_objects, user_id=user_id)

        user_activity_group_instance_dtos = [
            self._convert_user_activity_group_instance_to_dto(each)
            for each in user_activity_group_instances
        ]

        return user_activity_group_instance_dtos

    def get_user_activity_group_instances_metric_tracker(
            self, user_activity_group_instance_ids: List[str]) -> \
            List[UserActivityGroupInstanceMetricTrackerDTO]:
        user_activity_group_instance_metric_trackers = \
            UserActivityGroupInstanceMetricTracker.objects.\
            select_for_update().filter(
                user_activity_group_instance_id__in=
                user_activity_group_instance_ids,
            )
        user_activity_group_instance_metric_tracker_dtos = [
            self._convert_user_ag_instance_metric_tracker_object_to_dto(each)
            for each in user_activity_group_instance_metric_trackers
        ]

        return user_activity_group_instance_metric_tracker_dtos

    def get_user_activity_group_instances_metric_tracker_without_transaction(
            self, user_activity_group_instance_ids: List[str]) -> \
            List[UserActivityGroupInstanceMetricTrackerDTO]:
        user_activity_group_instance_metric_trackers = \
            UserActivityGroupInstanceMetricTracker.objects.filter(
                user_activity_group_instance_id__in=
                user_activity_group_instance_ids,
            )
        user_activity_group_instance_metric_tracker_dtos = [
            self._convert_user_ag_instance_metric_tracker_object_to_dto(each)
            for each in user_activity_group_instance_metric_trackers
        ]

        return user_activity_group_instance_metric_tracker_dtos

    def create_user_activity_group_instances(
            self, user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO]):
        user_activity_group_instances = [
            self._convert_user_activity_group_instance_dto_to_object(dto)
            for dto in user_activity_group_instance_dtos
        ]

        UserActivityGroupInstance.objects.bulk_create(
            user_activity_group_instances)

    def update_user_activity_group_instances(
            self, user_activity_group_instance_dtos:
            List[UserActivityGroupInstanceDTO]):
        user_activity_group_instances = [
            self._convert_user_activity_group_instance_dto_to_object(dto)
            for dto in user_activity_group_instance_dtos
        ]

        UserActivityGroupInstance.objects.bulk_update(
            user_activity_group_instances,
            ['completion_percentage', 'completion_status', 'instance_type',
             'last_update_datetime'])

    def get_activity_group_associations_for_activity_group_ids(
            self, activity_group_ids: List[str]) -> \
            List[ActivityGroupAssociationDTO]:
        activity_group_associations = ActivityGroupAssociation.objects.filter(
            activity_group_id__in=activity_group_ids)
        activity_group_association_dtos = [
            self._convert_activity_group_association_to_dto(each)
            for each in activity_group_associations
        ]
        return activity_group_association_dtos

    def create_user_activity_group_instances_metric_tracker(
            self, user_activity_group_instance_metric_dtos:
            List[UserActivityGroupInstanceMetricTrackerDTO]):
        user_activity_group_instance_metrics = [
            self._convert_user_ag_instance_metric_tracker_dto_to_object(dto)
            for dto in user_activity_group_instance_metric_dtos
        ]

        UserActivityGroupInstanceMetricTracker.objects.bulk_create(
            user_activity_group_instance_metrics)

    def update_user_activity_group_instances_metric_tracker(
            self, user_activity_group_instance_metric_dtos:
            List[UserActivityGroupInstanceMetricTrackerDTO]):
        user_activity_group_instance_metrics = [
            self._convert_user_ag_instance_metric_tracker_dto_to_object(dto)
            for dto in user_activity_group_instance_metric_dtos
        ]
        UserActivityGroupInstanceMetricTracker.objects.bulk_update(
            user_activity_group_instance_metrics,
            ['current_value', 'last_update_datetime'])

    def get_all_activity_group_ids(self) -> List[str]:
        activity_group_ids = ActivityGroup.objects.values_list("id", flat=True)
        return list(map(str, activity_group_ids))

    def get_existing_activity_group_ids(self, activity_group_ids: List[str]) \
            -> List[str]:
        existing_activity_group_ids = ActivityGroup.objects.filter(
            id__in=activity_group_ids).values_list('id', flat=True)
        return list(map(str, existing_activity_group_ids))

    def create_activity_group_associations(
            self, activity_group_association_dtos:
            List[ActivityGroupAssociationDTO]):
        activity_group_associations = [
            self._convert_activity_group_association_dto_to_object(each)
            for each in activity_group_association_dtos
        ]

        ActivityGroupAssociation.objects.bulk_create(
            activity_group_associations)

    def get_existing_completion_metric_ids(
            self, completion_metric_ids: List[str]) -> List[str]:
        existing_completion_metric_ids = CompletionMetric.objects.filter(
            id__in=completion_metric_ids).values_list("id", flat=True)
        return list(map(str, existing_completion_metric_ids))

    def get_existing_reward_config_ids(
            self, reward_config_ids: List[str]) -> List[str]:
        existing_reward_config_ids = RewardConfig.objects.filter(
            id__in=reward_config_ids).values_list("id", flat=True)
        return list(map(str, existing_reward_config_ids))

    def create_activity_groups(
            self, activity_group_dtos: List[CreateActivityGroupDTO]):
        activity_groups = [
            ActivityGroup(
                id=dto.id,
                name=dto.name,
                description=dto.description,
            )
            for dto in activity_group_dtos
        ]

        ActivityGroup.objects.bulk_create(activity_groups)

        for dto in activity_group_dtos:
            frequency_config = FrequencyConfig.objects.create(
                frequency_type=dto.frequency_type,
                config=dto.frequency_config,
            )
            activity_group_config = ActivityGroupConfig.objects.create(
                activity_group_id=dto.id, frequency_config=frequency_config)
            reward_configs = RewardConfig.objects.filter(
                id__in=dto.reward_config_ids)
            activity_group_config.reward_config.add(*list(reward_configs))

    def create_reward_configs(
            self, reward_config_dtos: List[RewardConfigDTO]):
        reward_configs = [
            RewardConfig(
                id=dto.id,
                resource_reward_config_id=dto.resource_reward_config_id,
            )
            for dto in reward_config_dtos
        ]

        RewardConfig.objects.bulk_create(reward_configs)

    def create_completion_metrics(
            self, completion_metric_dtos: List[CompletionMetricDTO]):
        completion_metrics = [
            CompletionMetric(
                id=dto.id,
                entity_id=dto.entity_id,
                entity_type=dto.entity_type,
                value=round(dto.value, 2),
            )
            for dto in completion_metric_dtos
        ]

        CompletionMetric.objects.bulk_create(completion_metrics)

        completion_metric_id_wise_completion_metric_object = {
            str(each.id): each
            for each in completion_metrics
        }

        activity_group_id_wise_completion_metric_ids = defaultdict(list)
        for dto in completion_metric_dtos:
            for activity_group_id in dto.activity_group_ids:
                activity_group_id_wise_completion_metric_ids[
                    activity_group_id].append(dto.id)

        for activity_group_id, completion_metric_ids in \
                activity_group_id_wise_completion_metric_ids.items():
            activity_group_config = ActivityGroupConfig.objects.get(
                activity_group_id=activity_group_id)
            completion_metrics = [
                completion_metric_id_wise_completion_metric_object[
                    completion_metric_id]
                for completion_metric_id in completion_metric_ids
            ]
            activity_group_config.completion_metric.add(
                *list(completion_metrics))

    def get_existing_activity_group_association_ids(
            self, activity_group_association_entity_ids: List[str]) -> \
            List[str]:
        existing_activity_group_association_ids = \
            ActivityGroupAssociation.objects.filter(
                id__in=activity_group_association_entity_ids).values_list(
                "id", flat=True)
        return list(map(str, existing_activity_group_association_ids))

    def get_all_users_activity_group_instances(
            self, activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO],
    ) -> List[UserActivityGroupInstanceDTO]:
        filter_objects = None
        for dto in activity_group_instance_identifier_dtos:
            q_object = Q(activity_group_id=dto.activity_group_id,
                         instance_identifier=dto.instance_identifier)
            if filter_objects is None:
                filter_objects = q_object
            else:
                filter_objects |= q_object

        if not filter_objects:
            return []

        user_activity_group_instances = \
            UserActivityGroupInstance.objects.filter(filter_objects)

        user_activity_group_instance_dtos = [
            self._convert_user_activity_group_instance_to_dto(each)
            for each in user_activity_group_instances
        ]

        return user_activity_group_instance_dtos

    def get_activity_group_instance_user_ids_for_instance_type(
            self, activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO],
            instance_type: InstanceTypeEnum) -> List[str]:
        filter_objects = None
        for dto in activity_group_instance_identifier_dtos:
            q_object = Q(activity_group_id=dto.activity_group_id,
                         instance_identifier=dto.instance_identifier)
            if filter_objects is None:
                filter_objects = q_object
            else:
                filter_objects |= q_object

        if not filter_objects:
            return []

        user_ids = UserActivityGroupInstance.objects.filter(
            filter_objects, instance_type=instance_type).values_list(
            'user_id', flat=True)

        return list(user_ids)

    @staticmethod
    def _convert_user_activity_group_instance_to_dto(
            user_activity_group_instance: UserActivityGroupInstance,
    ) -> UserActivityGroupInstanceDTO:
        return UserActivityGroupInstanceDTO(
            id=str(user_activity_group_instance.id),
            user_id=user_activity_group_instance.user_id,
            instance_identifier=
            user_activity_group_instance.instance_identifier,
            instance_type=user_activity_group_instance.instance_type,
            activity_group_id=
            str(user_activity_group_instance.activity_group_id),
            completion_percentage=
            user_activity_group_instance.completion_percentage,
            completion_status=user_activity_group_instance.completion_status,
        )

    @staticmethod
    def _convert_user_ag_instance_metric_tracker_object_to_dto(
            user_activity_group_instance_metric_tracker:
            UserActivityGroupInstanceMetricTracker,
    ) -> UserActivityGroupInstanceMetricTrackerDTO:
        activity_group_completion_metric_id = \
            user_activity_group_instance_metric_tracker.\
            activity_group_completion_metric_id
        activity_group_optional_metric_id = \
            user_activity_group_instance_metric_tracker.\
            activity_group_optional_metric_id

        if activity_group_completion_metric_id:
            activity_group_completion_metric_id = str(
                activity_group_completion_metric_id)

        if activity_group_optional_metric_id:
            activity_group_optional_metric_id = str(
                activity_group_optional_metric_id)

        return UserActivityGroupInstanceMetricTrackerDTO(
            id=str(user_activity_group_instance_metric_tracker.id),
            user_activity_group_instance_id=
            str(user_activity_group_instance_metric_tracker
                .user_activity_group_instance_id),
            activity_group_completion_metric_id=
            activity_group_completion_metric_id,
            current_value=
            round(
                user_activity_group_instance_metric_tracker.current_value, 2,
            ),
            activity_group_optional_metric_id=activity_group_optional_metric_id,
        )

    @staticmethod
    def _convert_user_activity_group_instance_dto_to_object(
            user_activity_group_instance_dto:
            UserActivityGroupInstanceDTO,
    ) -> UserActivityGroupInstance:
        return UserActivityGroupInstance(
            id=user_activity_group_instance_dto.id,
            instance_identifier=user_activity_group_instance_dto
            .instance_identifier,
            instance_type=user_activity_group_instance_dto.instance_type,
            user_id=user_activity_group_instance_dto.user_id,
            activity_group_id=user_activity_group_instance_dto
            .activity_group_id,
            completion_percentage=user_activity_group_instance_dto
            .completion_percentage,
            completion_status=
            user_activity_group_instance_dto.completion_status,
            last_update_datetime=get_current_local_date_time(),
        )

    @staticmethod
    def _convert_user_ag_instance_metric_tracker_dto_to_object(
            user_activity_group_instance_metric_tracker_dto:
            UserActivityGroupInstanceMetricTrackerDTO,
    ) -> UserActivityGroupInstanceMetricTracker:
        return UserActivityGroupInstanceMetricTracker(
                id=user_activity_group_instance_metric_tracker_dto.id,
                user_activity_group_instance_id=
                user_activity_group_instance_metric_tracker_dto.
                user_activity_group_instance_id,
                activity_group_completion_metric_id=
                user_activity_group_instance_metric_tracker_dto.
                activity_group_completion_metric_id,
                current_value=
                round(user_activity_group_instance_metric_tracker_dto
                      .current_value, 2),
                last_update_datetime=get_current_local_date_time(),
                activity_group_optional_metric_id=
                user_activity_group_instance_metric_tracker_dto
                .activity_group_optional_metric_id,
            )

    @staticmethod
    def _convert_activity_group_association_to_dto(
            activity_group_association: ActivityGroupAssociation) -> \
            ActivityGroupAssociationDTO:
        return ActivityGroupAssociationDTO(
            id=str(activity_group_association.id),
            activity_group_id=str(
                activity_group_association.activity_group_id),
            association_id=str(activity_group_association.association_id),
            association_type=activity_group_association.association_type,
        )

    @staticmethod
    def _convert_activity_group_association_dto_to_object(
            activity_group_association_dto: ActivityGroupAssociationDTO) -> \
            ActivityGroupAssociation:
        return ActivityGroupAssociation(
            id=activity_group_association_dto.id,
            activity_group_id=activity_group_association_dto.activity_group_id,
            association_id=activity_group_association_dto.association_id,
            association_type=activity_group_association_dto.association_type,
        )

    @staticmethod
    def _latest_user_activity_group_instance_reward_ids(
            user_ag_instance_id_reward_config_id_dtos:
            List[UserAGInstanceIdAGRewardConfigIdDTO]):
        filter_objects = None
        for dto in user_ag_instance_id_reward_config_id_dtos:
            q_object = Q(
                user_activity_group_instance_id=
                dto.user_activity_group_instance_id,
                activity_group_reward_config_id=
                dto.activity_group_reward_config_id,
            )
            if filter_objects is None:
                filter_objects = q_object
            else:
                filter_objects |= q_object

        latest_user_activity_group_instance_reward = \
            UserActivityGroupInstanceReward.objects.filter(
                user_activity_group_instance_id=
                OuterRef('user_activity_group_instance_id'),
                activity_group_reward_config_id=
                OuterRef('activity_group_reward_config_id'),
            ).order_by('-creation_datetime')[:1]

        user_activity_group_instance_rewards = \
            UserActivityGroupInstanceReward.objects.filter(
                filter_objects,
            ).values(
                "user_activity_group_instance_id",
                "activity_group_reward_config_id",
            ).annotate(
                latest_user_activity_group_instance_reward_id=Subquery(
                    latest_user_activity_group_instance_reward.values('id'),
                ),
            )

        latest_user_activity_group_instance_reward_ids = [
            str(each['latest_user_activity_group_instance_reward_id'])
            for each in user_activity_group_instance_rewards
        ]

        return latest_user_activity_group_instance_reward_ids

    @staticmethod
    def _convert_user_activity_group_instance_reward_objs_into_dtos(
            latest_user_activity_group_instance_rewards:
            List[UserActivityGroupInstanceReward],
    ) -> List[UserActivityGroupInstanceRewardDTO]:
        user_activity_group_instance_reward_dtos = [
            UserActivityGroupInstanceRewardDTO(
                id=str(each.id),
                user_activity_group_instance_id=
                str(each.user_activity_group_instance_id),
                activity_group_reward_config_id=
                str(each.activity_group_reward_config_id),
                rewarded_at_value=each.rewarded_at_value,
            )
            for each in latest_user_activity_group_instance_rewards
        ]

        return user_activity_group_instance_reward_dtos

    def get_activity_groups_optional_metrics(
            self, activity_group_ids: List[str]) -> \
            List[ActivityGroupOptionalMetricDTO]:
        activity_group_configs = ActivityGroupConfig.objects.filter(
            activity_group_id__in=activity_group_ids).prefetch_related(
            'optional_metric')

        activity_group_optional_metrics = []
        for each in activity_group_configs:
            if not each.optional_metric:
                continue

            optional_metrics = each.optional_metric.all()
            for optional_metric in optional_metrics:
                activity_group_optional_metrics.append(
                    ActivityGroupOptionalMetricDTO(
                        id=str(optional_metric.id),
                        activity_group_id=str(each.activity_group_id),
                        entity_id=optional_metric.entity_id,
                        entity_type=optional_metric.entity_type,
                    ),
                )
        return activity_group_optional_metrics

    def get_streak_enabled_activity_group_ids(self) -> List[str]:
        activity_group_ids = ActivityGroupConfig.objects.filter(
            should_consider_for_streak=True,
        ).values_list('activity_group_id', flat=True)
        return list(map(str, activity_group_ids))

    def get_user_activity_group_streak_details(self, user_id: str) -> \
            List[UserActivityGroupStreakDTO]:
        user_activity_group_streaks = UserActivityGroupStreak.objects.filter(
            user_id=user_id)
        user_activity_group_streak_dtos = [
            self._convert_activity_group_streak_to_dto(each)
            for each in user_activity_group_streaks
        ]
        return user_activity_group_streak_dtos

    def get_user_activity_group_streaks(
            self, user_id: str, activity_group_ids: List[str],
    ) -> List[UserActivityGroupStreakDTO]:
        user_activity_group_streaks = \
            UserActivityGroupStreak.objects.select_for_update().filter(
                user_id=user_id, activity_group_id__in=activity_group_ids)
        user_activity_group_streak_dtos = [
            self._convert_activity_group_streak_to_dto(each)
            for each in user_activity_group_streaks
        ]
        return user_activity_group_streak_dtos

    def create_user_activity_groups_streak(
            self, user_activity_group_streak_dtos:
            List[UserActivityGroupStreakDTO]):
        user_activity_group_streaks = [
            UserActivityGroupStreak(
                id=dto.id,
                user_id=dto.user_id,
                activity_group_id=dto.activity_group_id,
                current_streak_count=dto.streak_count,
                max_streak_count=dto.max_streak_count,
                last_updated_at=dto.last_updated_at,
            )
            for dto in user_activity_group_streak_dtos
        ]

        UserActivityGroupStreak.objects.bulk_create(
            user_activity_group_streaks)

    def update_user_activity_groups_streak(
            self, user_activity_group_streak_dtos:
            List[UserActivityGroupStreakDTO]):
        user_activity_group_streaks = [
            UserActivityGroupStreak(
                id=dto.id,
                user_id=dto.user_id,
                activity_group_id=dto.activity_group_id,
                current_streak_count=dto.streak_count,
                max_streak_count=dto.max_streak_count,
                last_updated_at=dto.last_updated_at,
            )
            for dto in user_activity_group_streak_dtos
        ]

        UserActivityGroupStreak.objects.bulk_update(
            user_activity_group_streaks,
            ["current_streak_count", "max_streak_count", "last_updated_at"])

    def get_activity_group_instance_user_ids_for_instance_types(
            self, activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO],
            instance_types: List[InstanceTypeEnum],
            user_ids: List[str],
    ) -> List[str]:
        filter_objects = None
        for user_id in user_ids:
            for dto in activity_group_instance_identifier_dtos:
                q_object = Q(activity_group_id=dto.activity_group_id,
                             instance_identifier=dto.instance_identifier,
                             user_id=user_id)
                if filter_objects is None:
                    filter_objects = q_object
                else:
                    filter_objects |= q_object

        if not filter_objects:
            return []

        user_ids = UserActivityGroupInstance.objects.filter(
            filter_objects, instance_type__in=instance_types,
        ).values_list('user_id', flat=True)

        return list(user_ids)

    def get_users_activity_group_instances(
            self, user_ids: List[str], activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO],
    ) -> List[UserActivityGroupInstanceDTO]:
        filter_objects = None
        for dto in activity_group_instance_identifier_dtos:
            q_object = Q(activity_group_id=dto.activity_group_id,
                         instance_identifier=dto.instance_identifier)
            if filter_objects is None:
                filter_objects = q_object
            else:
                filter_objects |= q_object

        if not filter_objects:
            return []

        user_activity_group_instances = \
            UserActivityGroupInstance.objects.filter(
                filter_objects, user_id__in=user_ids)

        user_activity_group_instance_dtos = [
            self._convert_user_activity_group_instance_to_dto(each)
            for each in user_activity_group_instances
        ]

        return user_activity_group_instance_dtos

    def delete_user_activity_group_instances(
            self, user_activity_group_instance_ids: List[str]):
        UserActivityGroupInstance.objects.filter(
            id__in=user_activity_group_instance_ids).delete()

    def get_user_activity_group_streak_details_with_transaction(
            self, user_id: str) -> List[UserActivityGroupStreakDTO]:
        user_activity_group_streaks = \
            UserActivityGroupStreak.objects.select_for_update().filter(
                user_id=user_id)
        user_activity_group_streak_dtos = [
            self._convert_activity_group_streak_to_dto(each)
            for each in user_activity_group_streaks
        ]
        return user_activity_group_streak_dtos

    def get_max_streak_for_user_ids(self, user_ids: List[str]) -> int:
        max_current_streak = UserActivityGroupStreak.objects.filter(
            user_id__in=user_ids,
        ).aggregate(
            max_streak=Max('max_streak_count'),
        )
        max_streak_value = max_current_streak['max_streak']

        return max_streak_value

    def update_user_activity_group_streak_last_updated_at(
            self, user_id: str, last_updated_at: datetime.datetime):
        UserActivityGroupStreak.objects.filter(
            user_id=user_id).update(last_updated_at=last_updated_at)

    def get_user_activity_group_streaks_up_to_max_rank(
            self, user_ids: List[str], activity_group_ids: List[str],
            max_rank: int) -> List[UserActivityGroupStreakDTO]:
        user_activity_group_streak_dtos = []
        for activity_group_id in activity_group_ids:
            max_streak_objs = UserActivityGroupStreak.objects.filter(
                user_id__in=user_ids,
                activity_group=activity_group_id,
            ).order_by('-current_streak_count')[:max_rank]
            user_activity_group_streak_dtos += [
                self._convert_activity_group_streak_to_dto(each)
                for each in max_streak_objs
            ]
        return user_activity_group_streak_dtos

    def get_user_activity_group_streak_for_given_streak(
            self, activity_group_ids: List[str], streak: int) -> \
            List[UserActivityGroupStreakDTO]:
        user_activity_group_streak_objs = \
            UserActivityGroupStreak.objects.filter(
                activity_group_id__in=activity_group_ids,
                current_streak_count=streak)
        user_activity_group_streak_dtos = [
            self._convert_activity_group_streak_to_dto(each)
            for each in user_activity_group_streak_objs
        ]
        return user_activity_group_streak_dtos

    def get_user_activity_group_streaks_for_user_ids(
            self, user_ids: List[str], activity_group_ids: List[str],
    ) -> List[UserActivityGroupStreakDTO]:

        user_activity_group_streaks = \
            UserActivityGroupStreak.objects.filter(
                user_id__in=user_ids,
                activity_group__in=activity_group_ids,
            )

        user_activity_group_streak_dtos = [
            self._convert_activity_group_streak_to_dto(each)
            for each in user_activity_group_streaks
        ]
        return user_activity_group_streak_dtos

    @staticmethod
    def _convert_activity_group_streak_to_dto(
            user_activity_group_streak: UserActivityGroupStreak,
    ) -> UserActivityGroupStreakDTO:
        return UserActivityGroupStreakDTO(
            id=str(user_activity_group_streak.id),
            user_id=user_activity_group_streak.user_id,
            streak_count=user_activity_group_streak.current_streak_count,
            activity_group_id=str(
                user_activity_group_streak.activity_group_id),
            max_streak_count=user_activity_group_streak.max_streak_count,
            last_updated_at=user_activity_group_streak.last_updated_at,
        )

    def get_user_activity_group_instances_of_given_types(
            self, user_id: str, activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO],
            instance_types: List[InstanceTypeEnum]) \
            -> List[UserActivityGroupInstanceDTO]:
        filter_objects = None
        for dto in activity_group_instance_identifier_dtos:
            q_object = Q(activity_group_id=dto.activity_group_id,
                         instance_identifier=dto.instance_identifier)
            if filter_objects is None:
                filter_objects = q_object
            else:
                filter_objects |= q_object

        if not filter_objects:
            return []

        user_activity_group_instances = \
            UserActivityGroupInstance.objects.filter(
                filter_objects, user_id=user_id,
                instance_type__in=instance_types)

        user_activity_group_instance_dtos = [
            self._convert_user_activity_group_instance_to_dto(each)
            for each in user_activity_group_instances
        ]

        return user_activity_group_instance_dtos

    def get_agi_user_ids_for_instance_types_completion_types(
            self, activity_group_instance_identifier_dtos:
            List[ActivityGroupInstanceIdentifierDTO],
            instance_types: List[InstanceTypeEnum], user_ids: List[str],
            completion_types: List[CompletionStatusEnum]) -> List[str]:
        filter_objects = None
        for user_id in user_ids:
            for dto in activity_group_instance_identifier_dtos:
                q_object = Q(activity_group_id=dto.activity_group_id,
                             instance_identifier=dto.instance_identifier,
                             user_id=user_id)
                if filter_objects is None:
                    filter_objects = q_object
                else:
                    filter_objects |= q_object

        if not filter_objects:
            return []

        user_ids = UserActivityGroupInstance.objects.filter(
            filter_objects, instance_type__in=instance_types,
            completion_status__in=completion_types
        ).values_list('user_id', flat=True)

        return list(user_ids)

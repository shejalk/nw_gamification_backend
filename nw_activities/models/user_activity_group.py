from django.core.exceptions import ValidationError
from django.db import models
from ib_common.models import AbstractDateTimeModel

from nw_activities.constants.enum import CompletionStatusEnum, \
    InstanceTypeEnum
from nw_activities.constants.exception_messages import \
    INVALID_COMPLETION_STATUS, INVALID_INSTANCE_TYPE
from nw_activities.models.activity_group import ActivityGroup
from nw_activities.models.configuration_models import RewardConfig, \
    CompletionMetric, OptionalMetric
from nw_activities.utils.generate_uuid import generate_uuid


def validate_completion_status(value):
    if value not in CompletionStatusEnum.get_list_of_values():
        raise ValidationError(INVALID_COMPLETION_STATUS.format(value))


def validate_instance_type(value):
    if value not in InstanceTypeEnum.get_list_of_values():
        raise ValidationError(INVALID_INSTANCE_TYPE.format(value))


class UserActivityGroupInstance(AbstractDateTimeModel):
    id = models.UUIDField(primary_key=True, default=generate_uuid,
                          editable=False)
    instance_identifier = models.CharField(max_length=50)
    instance_type = models.CharField(
        max_length=50, validators=[validate_instance_type])
    user_id = models.CharField(max_length=36)
    activity_group = models.ForeignKey(ActivityGroup, on_delete=models.CASCADE)
    completion_percentage = models.FloatField()
    completion_status = models.CharField(
        max_length=50, validators=[validate_completion_status])

    class Meta:
        unique_together = ("user_id", "activity_group", "instance_identifier")
        index_together = ("activity_group", "instance_identifier")
        app_label = "nw_activities"


class UserActivityGroupInstanceMetricTracker(AbstractDateTimeModel):
    id = models.UUIDField(primary_key=True, default=generate_uuid,
                          editable=False)
    user_activity_group_instance = models.ForeignKey(
        UserActivityGroupInstance, on_delete=models.CASCADE)
    activity_group_completion_metric = models.ForeignKey(
        CompletionMetric, on_delete=models.CASCADE, null=True, blank=True)
    activity_group_optional_metric = models.ForeignKey(
        OptionalMetric, on_delete=models.CASCADE, null=True, blank=True)
    current_value = models.FloatField()

    class Meta:
        unique_together = (
            ("user_activity_group_instance", "activity_group_optional_metric",
             "activity_group_completion_metric")
        )
        app_label = "nw_activities"


class UserActivityGroupInstanceReward(AbstractDateTimeModel):
    id = models.UUIDField(primary_key=True, default=generate_uuid,
                          editable=False)
    user_activity_group_instance = models.ForeignKey(
        UserActivityGroupInstance, on_delete=models.CASCADE)
    activity_group_reward_config = models.ForeignKey(
        RewardConfig, on_delete=models.CASCADE)
    rewarded_at_value = models.FloatField()

    class Meta:
        app_label = "nw_activities"


class UserActivityGroupStreak(AbstractDateTimeModel):
    id = models.UUIDField(primary_key=True, default=generate_uuid,
                          editable=False)
    activity_group = models.ForeignKey(ActivityGroup, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=36)
    current_streak_count = models.IntegerField()
    max_streak_count = models.IntegerField()
    last_updated_at = models.DateTimeField()

    class Meta:
        app_label = "nw_activities"
        unique_together = ("user_id", "activity_group")

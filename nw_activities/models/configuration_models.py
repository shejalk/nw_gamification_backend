from django.core.exceptions import ValidationError
from django.db import models
from ib_common.models import AbstractDateTimeModel

from nw_activities.constants.enum import FrequencyTypeEnum, OperatorEnum, \
    CompletionMetricEntityTypeEnum, OptionalMetricEntityTypeEnum
from nw_activities.constants.exception_messages import \
    INVALID_FREQUENCY_TYPE, INVALID_CONDITIONAL_OPERATOR, \
    INVALID_ACTIVITY_GROUP_COMPLETION_METRIC_ENTITY_TYPE, \
    INVALID_ACTIVITY_GROUP_OPTIONAL_METRIC_ENTITY_TYPE
from nw_activities.models.activity_group import ActivityGroup
from nw_activities.utils.generate_uuid import generate_uuid


def validate_frequency_type(value):
    if value not in FrequencyTypeEnum.get_list_of_values():
        raise ValidationError(INVALID_FREQUENCY_TYPE.format(value))


def validate_operator(value):
    if value not in OperatorEnum.get_list_of_values():
        raise ValidationError(INVALID_CONDITIONAL_OPERATOR.format(value))


def validate_activity_group_completion_metric_entity_type(value):
    if value not in CompletionMetricEntityTypeEnum.get_list_of_values():
        raise ValidationError(
            INVALID_ACTIVITY_GROUP_COMPLETION_METRIC_ENTITY_TYPE.format(value))


def validate_activity_group_optional_metric_entity_type(value):
    if value not in OptionalMetricEntityTypeEnum.get_list_of_values():
        raise ValidationError(
            INVALID_ACTIVITY_GROUP_OPTIONAL_METRIC_ENTITY_TYPE.format(value))


class RewardConfig(AbstractDateTimeModel):
    id = models.UUIDField(primary_key=True, default=generate_uuid,
                          editable=False)
    resource_reward_config_id = models.CharField(max_length=36, unique=True)

    class Meta:
        app_label = "nw_activities"


class FrequencyConfig(AbstractDateTimeModel):
    id = models.UUIDField(primary_key=True, default=generate_uuid,
                          editable=False)
    frequency_type = models.CharField(
        max_length=50, validators=[validate_frequency_type])
    config = models.TextField()

    class Meta:
        app_label = "nw_activities"


class CompletionMetric(AbstractDateTimeModel):
    id = models.UUIDField(primary_key=True, default=generate_uuid,
                          editable=False)
    entity_id = models.CharField(max_length=36)
    entity_type = models.CharField(
        max_length=50,
        validators=[validate_activity_group_completion_metric_entity_type],
    )
    value = models.FloatField()

    class Meta:
        app_label = "nw_activities"


class OptionalMetric(AbstractDateTimeModel):
    id = models.UUIDField(primary_key=True, default=generate_uuid,
                          editable=False)
    entity_id = models.CharField(max_length=36)
    entity_type = models.CharField(
        max_length=50,
        validators=[validate_activity_group_optional_metric_entity_type],
    )

    class Meta:
        app_label = "nw_activities"


class ActivityGroupConfig(AbstractDateTimeModel):
    id = models.UUIDField(primary_key=True, default=generate_uuid,
                          editable=False)
    activity_group = models.OneToOneField(
        ActivityGroup, on_delete=models.CASCADE)
    reward_config = models.ManyToManyField(RewardConfig)
    frequency_config = models.OneToOneField(
        FrequencyConfig, on_delete=models.CASCADE)
    completion_metric = models.ManyToManyField(CompletionMetric)
    optional_metric = models.ManyToManyField(OptionalMetric)
    should_consider_for_streak = models.BooleanField(default=False)

    class Meta:
        app_label = "nw_activities"

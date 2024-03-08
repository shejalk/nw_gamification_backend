from django import forms
from django.contrib import admin
from django.contrib.admin import register

from nw_activities.models import Activity, ActivityGroup, \
    ActivityGroupAssociation, RewardConfig, FrequencyConfig, \
    CompletionMetric, ActivityGroupConfig, UserActivityLog, \
    UserActivityGroupInstance, UserActivityGroupInstanceMetricTracker, \
    UserActivityGroupInstanceReward, UserActivityGroupStreak
from nw_activities.models.configuration_models import OptionalMetric


@register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['name_enum', 'name', 'description']
    search_fields = ['name_enum']


@register(ActivityGroup)
class ActivityGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    search_fields = ['id']


@register(ActivityGroupAssociation)
class ActivityGroupAssociationAdmin(admin.ModelAdmin):
    list_display = ['id', 'activity_group_id', 'association_id',
                    'association_type']
    list_filter = ['association_type']
    search_fields = ['id', 'activity_group__id', 'association_id']


@register(RewardConfig)
class RewardConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'resource_reward_config_id']
    search_fields = ['resource_reward_config_id']


@register(FrequencyConfig)
class FrequencyConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'frequency_type']
    list_filter = ['frequency_type']
    search_fields = ['id']


@register(CompletionMetric)
class CompletionMetricAdmin(admin.ModelAdmin):
    list_display = ['id', 'entity_id', 'entity_type', 'value']
    list_filter = ['entity_type']
    search_fields = ['id', 'entity_type']


class ActivityGroupConfigForm(forms.ModelForm):
    completion_metrics = forms.ModelMultipleChoiceField(
        queryset=CompletionMetric.objects.all(), required=False)
    reward_configs = forms.ModelMultipleChoiceField(
        queryset=RewardConfig.objects.all(), required=False)


@register(ActivityGroupConfig)
class ActivityGroupConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'activity_group_id']
    search_fields = ['id', 'activity_group__id']

    form = ActivityGroupConfigForm


@register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'activity_id', 'entity_id', 'entity_type',
                    'resource_name_enum', 'resource_value', 'transaction_type']
    list_filter = ['resource_name_enum', 'entity_type', 'transaction_type']
    search_fields = ['id', 'user_id', 'activity__name_enum']


@register(UserActivityGroupInstance)
class UserActivityGroupInstanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'instance_identifier', 'user_id', 'instance_type',
                    'activity_group_id', 'completion_percentage',
                    'completion_status']
    list_filter = ['completion_status']
    search_fields = ['id', 'activity_group__id', 'user_id']


@register(UserActivityGroupInstanceMetricTracker)
class UserActivityGroupInstanceMetricTrackerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_activity_group_instance_id', 'user_id',
                    'activity_group_completion_metric_id', 'current_value',
                    'last_update_datetime', 'activity_group_optional_metric_id']
    search_fields = ['user_activity_group_instance__user_id']

    @staticmethod
    def user_id(obj):
        return obj.user_activity_group_instance.user_id

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user_activity_group_instance')


@register(UserActivityGroupInstanceReward)
class UserActivityGroupInstanceRewardAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_activity_group_instance_id', 'user_id',
                    'activity_group_reward_config_id', 'rewarded_at_value',
                    'creation_datetime']
    search_fields = ['user_activity_group_instance__user_id']

    @staticmethod
    def user_id(obj):
        return obj.user_activity_group_instance.user_id

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user_activity_group_instance')


@register(OptionalMetric)
class OptionalMetricAdmin(admin.ModelAdmin):
    list_display = ['id', 'entity_id', 'entity_type']
    list_filter = ['entity_type']
    search_fields = ['id', 'entity_type']


@register(UserActivityGroupStreak)
class UserActivityGroupStreakAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'activity_group_id', 'current_streak_count',
                    'max_streak_count', 'last_updated_at']
    search_fields = ['user_id']

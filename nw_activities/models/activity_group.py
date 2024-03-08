from django.core.exceptions import ValidationError
from django.db import models
from ib_common.models import AbstractDateTimeModel

from nw_activities.constants.enum import ActivityGroupAssociationTypeEnum
from nw_activities.constants.exception_messages import \
    INVALID_ACTIVITY_GROUP_ASSOCIATION
from nw_activities.utils.generate_uuid import generate_uuid


def validate_activity_group_association_type(value):
    if value not in ActivityGroupAssociationTypeEnum.get_list_of_values():
        raise ValidationError(INVALID_ACTIVITY_GROUP_ASSOCIATION.format(value))


class ActivityGroup(AbstractDateTimeModel):
    id = models.UUIDField(primary_key=True, default=generate_uuid,
                          editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    class Meta:
        app_label = "nw_activities"


class ActivityGroupAssociation(AbstractDateTimeModel):
    id = models.UUIDField(primary_key=True, default=generate_uuid,
                          editable=False)
    activity_group = models.ForeignKey(ActivityGroup, on_delete=models.CASCADE)
    association_id = models.CharField(max_length=36)
    association_type = models.CharField(
        max_length=50, validators=[validate_activity_group_association_type])

    class Meta:
        unique_together = ("activity_group", "association_id")
        app_label = "nw_activities"

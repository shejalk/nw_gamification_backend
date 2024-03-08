from django.core.exceptions import ValidationError
from django.db import models
from ib_common.models import AbstractDateTimeModel

from nw_activities.constants.enum import TransactionTypeEnum
from nw_activities.constants.exception_messages import INVALID_TRANSACTION_TYPE
from nw_activities.models.activity import Activity
from nw_activities.utils.generate_uuid import generate_uuid


def validate_transaction_type(value):
    if value not in TransactionTypeEnum.get_list_of_values():
        raise ValidationError(INVALID_TRANSACTION_TYPE.format(value))


class UserActivityLog(AbstractDateTimeModel):
    id = models.UUIDField(primary_key=True, default=generate_uuid,
                          editable=False)
    user_id = models.CharField(max_length=36, db_index=True)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    entity_id = models.CharField(max_length=36)
    entity_type = models.CharField(max_length=50)
    resource_name_enum = models.CharField(max_length=50)
    resource_value = models.FloatField()
    transaction_type = models.CharField(
        max_length=50, validators=[validate_transaction_type])

    class Meta:
        app_label = "nw_activities"

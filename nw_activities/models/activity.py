from django.db import models
from ib_common.models import AbstractDateTimeModel


class Activity(AbstractDateTimeModel):
    name_enum = models.CharField(primary_key=True, max_length=50,
                                 editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    class Meta:
        app_label = "nw_activities"

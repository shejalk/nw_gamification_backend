from django.apps import AppConfig


class NwActivitiesAppConfig(AppConfig):
    name = "nw_activities"

    def ready(self):
        from nw_activities import signals  # pylint: disable=W0611

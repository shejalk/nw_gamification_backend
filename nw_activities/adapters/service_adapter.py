class ServiceAdapter:

    @staticmethod
    def _is_app_installed(app_name: str):
        from django.apps import apps
        return apps.is_installed(app_name)

    @property
    def resources(self):
        from nw_activities.adapters.resources_service_adapter import \
            ResourceServiceAdapter
        return ResourceServiceAdapter()

    @property
    def clubs(self):
        from nw_activities.adapters.clubs_service_adapter import \
            ClubsServiceAdapter
        return ClubsServiceAdapter()

    @property
    def gamification_wrapper(self):
        app_name = 'nkb_gamification_wrapper'
        if self._is_app_installed(app_name):
            from nw_activities.adapters.gamification_wrapper_service. \
                gamification_wrapper import GamificationWrapperServiceAdapter
            return GamificationWrapperServiceAdapter()
        from nw_activities.adapters.gamification_wrapper_service \
            .gamification_wrapper_mock import \
            GamificationWrapperServiceAdapterMock
        return GamificationWrapperServiceAdapterMock()

    @property
    def ws_service(self):
        from nw_activities.adapters.ws_service_adapter import \
            WebSocketServiceAdapter
        return WebSocketServiceAdapter()

    @property
    def event_service(self):
        from nw_activities.adapters.events_service_adapter import \
            EventsServiceAdapter
        return EventsServiceAdapter()


def get_service_adapter():
    return ServiceAdapter()

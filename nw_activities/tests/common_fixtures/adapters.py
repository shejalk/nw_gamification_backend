from nw_activities.adapters.service_adapter import get_service_adapter
from nw_activities.tests.common_fixtures import get_mock_object


def send_activity_group_completed_event_mock(mocker):
    from nw_activities.adapters.ws_service_adapter import \
        WebSocketServiceAdapter
    func_to_mock = WebSocketServiceAdapter.send_activity_group_completed_event
    mock = get_mock_object(mocker, func_to_mock)
    return mock


def is_user_has_access_to_perform_activities_mock(mocker, return_value=None):
    adapter = get_service_adapter()
    func_to_mock = adapter.gamification_wrapper. \
        is_user_has_access_to_perform_activities
    mock = get_mock_object(mocker, func_to_mock)

    if return_value is not None:
        mock.return_value = return_value

    return mock


def is_streak_enabled_mock(mocker, return_value=None):
    adapter = get_service_adapter()
    func_to_mock = adapter.gamification_wrapper.is_streak_enabled
    mock = get_mock_object(mocker, func_to_mock)

    if return_value is not None:
        mock.return_value = return_value

    return mock


def update_user_resources_mock(mocker):
    from nw_activities.adapters.resources_service_adapter import \
        ResourceServiceAdapter
    func_to_mock = ResourceServiceAdapter.update_user_resources
    mock = get_mock_object(mocker, func_to_mock)
    return mock


def update_user_club_leaderboards_mock(mocker):
    from nw_activities.adapters.clubs_service_adapter import \
        ClubsServiceAdapter
    func_to_mock = ClubsServiceAdapter.update_user_club_leaderboards
    mock = get_mock_object(mocker, func_to_mock)
    return mock


def is_activity_groups_enabled_for_users_mock(mocker, return_value=None):
    adapter = get_service_adapter()
    func_to_mock = \
        adapter.gamification_wrapper.is_activity_groups_enabled_for_users
    mock = get_mock_object(mocker, func_to_mock)

    if return_value is not None:
        mock.return_value = return_value

    return mock


def update_user_resource_with_transaction_mock(mocker):
    from nw_activities.adapters.resources_service_adapter import \
        ResourceServiceAdapter
    func_to_mock = ResourceServiceAdapter.update_user_resource_with_transaction
    mock = get_mock_object(mocker, func_to_mock)

    return mock


def get_user_resource_mock(mocker):
    from nw_activities.adapters.resources_service_adapter import \
        ResourceServiceAdapter
    func_to_mock = ResourceServiceAdapter.get_user_resource
    mock = get_mock_object(mocker, func_to_mock)

    return mock


def get_reward_config_details_mock(mocker):
    from nw_activities.adapters.resources_service_adapter import \
        ResourceServiceAdapter
    func_to_mock = ResourceServiceAdapter.get_reward_config_details
    mock = get_mock_object(mocker, func_to_mock)

    return mock


def send_activity_group_streak_updated_ws_event_mock(mocker):
    from nw_activities.adapters.ws_service_adapter import \
        WebSocketServiceAdapter
    func_to_mock = WebSocketServiceAdapter.\
        send_activity_group_streak_updated_event
    mock = get_mock_object(mocker, func_to_mock)
    return mock


def send_activity_group_streak_updated_event_mock(mocker):
    from nw_activities.adapters.events_service_adapter import \
        EventsServiceAdapter
    func_to_mock = EventsServiceAdapter.\
        send_activity_group_streak_updated_event
    mock = get_mock_object(mocker, func_to_mock)
    return mock


def send_user_consistency_score_updated_event_mock(mocker):
    from nw_activities.adapters.events_service_adapter import \
        EventsServiceAdapter
    func_to_mock = EventsServiceAdapter. \
        send_user_consistency_score_updated_event
    mock = get_mock_object(mocker, func_to_mock)
    return mock


def update_leaderboard_for_streak_change_mock(mocker):
    from nw_activities.adapters.gamification_wrapper_service\
        .gamification_wrapper_mock import \
        GamificationWrapperServiceAdapterMock
    func_to_mock = GamificationWrapperServiceAdapterMock\
        .update_leaderboard_for_streak_change
    mock = get_mock_object(mocker, func_to_mock)
    return mock


def send_user_consistency_score_credited_event_mock(mocker):
    from nw_activities.adapters.ws_service_adapter import \
        WebSocketServiceAdapter
    func_to_mock = WebSocketServiceAdapter. \
        send_user_consistency_score_credited_event
    mock = get_mock_object(mocker, func_to_mock)
    return mock

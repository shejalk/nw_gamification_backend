from nw_activities.tests.common_fixtures import get_mock_object


def update_associations_completion_metrics_of_type_activity_group(mocker):
    from nw_activities.interactors.\
        update_activity_group_association_completion_metrics.activity_group \
        import ActivityGroupAssociationActivityGroupInteractor
    func_to_mock = ActivityGroupAssociationActivityGroupInteractor\
        .update_associations_completion_metrics_of_type_activity_group
    mock = get_mock_object(mocker, func_to_mock)
    return mock


def create_user_activity_group_instance_rewards_mock(mocker):
    from nw_activities.interactors\
        .create_user_activity_group_instance_rewards \
        import CreateUserActivityGroupInstanceRewardInteractor
    func_to_mock = CreateUserActivityGroupInstanceRewardInteractor\
        .create_user_activity_group_instance_rewards
    mock = get_mock_object(mocker, func_to_mock)
    return mock


def get_user_activity_group_instances_with_associations_instances_mock(mocker):
    from nw_activities.interactors.get_user_activity_group_instance_details \
        import GetUserActivityGroupInstanceInteractor
    func_to_mock = GetUserActivityGroupInstanceInteractor\
        .get_user_activity_group_instances_with_associations_instances
    mock = get_mock_object(mocker, func_to_mock)
    return mock


def update_associations_completion_metrics_of_type_activity_mock(mocker):
    from nw_activities.interactors.\
        update_activity_group_association_completion_metrics.activity import \
        ActivityGroupAssociationActivityInteractor
    func_to_mock = ActivityGroupAssociationActivityInteractor\
        .update_associations_completion_metrics_of_type_activity
    mock = get_mock_object(mocker, func_to_mock)
    return mock


def update_activity_groups_optional_metrics_mock(mocker):
    mock = mocker.patch(
        "nw_activities.interactors."
        "update_activity_group_optional_metrics.activity."
        "ActivityGroupAssociationActivityInteractor."
        "update_activity_groups_optional_metrics",
    )
    return mock


def get_user_streak_activity_group_instances_between_given_dates_mock(mocker):
    from nw_activities.interactors.get_user_activity_group_instance_details \
        import GetUserActivityGroupInstanceInteractor

    func_to_mock = GetUserActivityGroupInstanceInteractor \
        .get_user_streak_activity_group_instances_between_given_dates
    mock = get_mock_object(mocker, func_to_mock)

    return mock


def get_user_streak_activity_group_instances_in_given_dates_mock(mocker):
    from nw_activities.interactors.get_user_activity_group_instance_details \
        import GetUserActivityGroupInstanceInteractor

    func_to_mock = GetUserActivityGroupInstanceInteractor \
        .get_user_streak_activity_group_instances_for_given_dates

    mock = get_mock_object(mocker, func_to_mock)

    return mock


def create_user_activity_group_streak_instance_with_daily_frequency_mock(
        mocker):
    from nw_activities.interactors.create_user_activity_group_instances \
        import CreateUserActivityGroupInstanceInteractor

    func_to_mock = CreateUserActivityGroupInstanceInteractor \
        .create_user_activity_group_streak_instance_with_daily_frequency
    mock = get_mock_object(mocker, func_to_mock)

    return mock


def delete_user_activity_group_streak_instance_with_daily_frequency_mock(
        mocker):
    from nw_activities.interactors.create_user_activity_group_instances \
        import CreateUserActivityGroupInstanceInteractor

    func_to_mock = CreateUserActivityGroupInstanceInteractor \
        .delete_streak_users_activity_group_instances_with_daily_frequency
    mock = get_mock_object(mocker, func_to_mock)

    return mock

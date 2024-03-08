from zappa.asynchronous import task


@task
def update_leaderboard_for_streak_change_async(
        user_id: str, score_change: float,
        instance_datetime_str: str = None):
    from nw_activities.interactors.update_user_activity_group_streak import \
        UpdateUserActivityGroupStreakInteractor
    from nw_activities.storages.activity_group_storage_implementation \
        import ActivityGroupStorageImplementation
    from ib_common.date_time_utils.convert_string_to_local_date_time import \
        convert_string_to_local_date_time
    from nw_activities.constants.constants import DATE_TIME_FORMAT

    activity_group_storage = ActivityGroupStorageImplementation()
    interactor = UpdateUserActivityGroupStreakInteractor(
        activity_group_storage)

    instance_datetime = convert_string_to_local_date_time(
        instance_datetime_str, DATE_TIME_FORMAT)

    interactor.update_leaderboard_for_streak_change(
        user_id, score_change, instance_datetime)

from django_swagger_utils.drf_server.utils.decorator.interface_decorator \
    import validate_decorator
from .validator_class import ValidatorClass


@validate_decorator(validator_class=ValidatorClass)
def api_wrapper(*args, **kwargs):
    user_id = str(kwargs['user_dto'].user_id)
    request_body = kwargs['request_data']
    freeze_date = request_body['freeze_date']

    from nw_activities.interactors.cancel_user_streak_freeze import \
        CancelUserStreakFreezeInteractor
    from nw_activities.storages.activity_group_storage_implementation import \
        ActivityGroupStorageImplementation
    from nw_activities.presenters.streak_freeze_presenter_implementation import \
        StreakFreezePresenterImplementation

    activity_group_storage = ActivityGroupStorageImplementation()
    interactor = CancelUserStreakFreezeInteractor(activity_group_storage)
    presenter = StreakFreezePresenterImplementation()

    return interactor.cancel_user_streak_freeze_wrapper(user_id, freeze_date,
                                                        presenter)

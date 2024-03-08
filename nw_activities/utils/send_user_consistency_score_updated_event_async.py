from typing import List, Dict
from zappa.asynchronous import task
from nw_activities.adapters.resources_service_adapter import UserResourceDTO


@task
def send_user_consistency_score_updated_event_async(
        user_id: str, user_resource_dicts: List[Dict]):
    from nw_activities.interactors.update_user_activity_group_streak import \
        UpdateUserActivityGroupStreakInteractor
    from nw_activities.storages.activity_group_storage_implementation import \
        ActivityGroupStorageImplementation

    activity_group_storage = ActivityGroupStorageImplementation()
    _ = UpdateUserActivityGroupStreakInteractor(activity_group_storage)

    user_resource_dtos = []
    for user_resource_dict in user_resource_dicts:
        user_resource_dtos.append(
            UserResourceDTO(
                user_resource_id=user_resource_dict["user_resource_id"],
                final_value=user_resource_dict["final_value"],
                user_id=user_resource_dict["user_id"],
                resource_name_enum=user_resource_dict["resource_name_enum"],
            ),
        )
    # interactor.send_user_consistency_score_updated_event(
    #     user_id, user_resource_dtos)

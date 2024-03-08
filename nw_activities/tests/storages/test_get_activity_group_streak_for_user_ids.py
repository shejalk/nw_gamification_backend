import uuid

import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import ActivityGroupFactory, \
    UserActivityGroupStreakFactory
from nw_activities.tests.factories.storage_dtos import \
    UserActivityGroupStreakDTOFactory


@pytest.mark.django_db
class TestGetActivityGroupStreakForUserIds:
    def test_get_activity_group_streak_for_user_ids(self):
        user_ids = [str(uuid.uuid4()) for _ in range(5)]
        activity_group_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        user_ids_to_consider = user_ids[:3]
        activity_group_ids_to_consider = [activity_group_ids[0]]
        _ = [
            ActivityGroupFactory(id=activity_group_id)
            for activity_group_id in activity_group_ids
        ]
        user_activity_group_streak_objs = []
        for activity_group_id in activity_group_ids:
            for user_id in user_ids:
                user_activity_group_streak_objs.append(
                    UserActivityGroupStreakFactory(
                        user_id=user_id,
                        activity_group_id=activity_group_id,
                        current_streak_count=10,
                        max_streak_count=10,
                    ),
                )
        user_activity_group_streak_dtos = []
        for obj in user_activity_group_streak_objs:
            if obj.user_id in user_ids_to_consider and \
                    obj.activity_group_id in activity_group_ids_to_consider:
                user_activity_group_streak_dtos.append(
                    UserActivityGroupStreakDTOFactory(
                        id=str(obj.id),
                        user_id=obj.user_id,
                        activity_group_id=str(obj.activity_group_id),
                        streak_count=obj.current_streak_count,
                        max_streak_count=obj.max_streak_count,
                        last_updated_at=obj.last_updated_at,
                    ),
                )

        storage = ActivityGroupStorageImplementation()

        response = storage.get_user_activity_group_streaks_for_user_ids(
            user_ids_to_consider, activity_group_ids_to_consider)

        sorted_response = sorted(
            response, key=lambda x: x.user_id,
        )
        sorted_user_activity_group_streak_dtos = sorted(
            user_activity_group_streak_dtos, key=lambda x: x.user_id,
        )

        assert sorted_response == sorted_user_activity_group_streak_dtos

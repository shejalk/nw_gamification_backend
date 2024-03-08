import uuid

import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import ActivityGroupFactory, \
    UserActivityGroupStreakFactory
from nw_activities.tests.factories.storage_dtos import \
    UserActivityGroupStreakDTOFactory


@pytest.mark.django_db
class TestGetUserActivityGroupStreaksUpToMaxRank:
    def test_get_user_activity_group_streaks_up_to_max_rank(self):
        user_ids = [str(uuid.uuid4()) for _ in range(7)]
        user_ids_to_consider = user_ids[:5]
        activity_group_ids = [str(uuid.uuid4())]
        max_rank = 5
        max_streak = 15
        streak_counts = [5, 7, 2, 3, 12, 6, 4]
        activity_group = ActivityGroupFactory(id=activity_group_ids[0])
        user_activity_group_streak_objs = []
        for i in range(7):
            user_activity_group_streak_objs.append(
                UserActivityGroupStreakFactory(
                    user_id=user_ids[i],
                    activity_group=activity_group,
                    current_streak_count=streak_counts[i],
                    max_streak_count=max_streak,
                ),
            )

        user_ag_streak_objs_to_consider = user_activity_group_streak_objs[:5]
        user_ag_streak_objs_to_consider.sort(
            key=lambda obj: obj.current_streak_count, reverse=True,
        )
        user_activity_group_streak_dtos = [
            UserActivityGroupStreakDTOFactory(
                id=str(obj.id),
                user_id=obj.user_id,
                activity_group_id=str(obj.activity_group_id),
                streak_count=obj.current_streak_count,
                max_streak_count=obj.max_streak_count,
                last_updated_at=obj.last_updated_at,
            )
            for obj in user_ag_streak_objs_to_consider
        ]

        storage = ActivityGroupStorageImplementation()

        response = storage.get_user_activity_group_streaks_up_to_max_rank(
            user_ids_to_consider, activity_group_ids, max_rank,
        )

        assert response == user_activity_group_streak_dtos

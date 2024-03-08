import uuid

import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import ActivityGroupFactory, \
    UserActivityGroupStreakFactory
from nw_activities.tests.factories.storage_dtos import \
    UserActivityGroupStreakDTOFactory


@pytest.mark.django_db
class TestGetUserActivityGroupStreakForGivenStreak:
    def test_get_user_activity_group_streak_for_given_streak(self):
        user_ids = [str(uuid.uuid4()) for _ in range(5)]
        activity_group_ids = [str(uuid.uuid4())]
        streak = 5
        streak_counts = [5, 7, 5, 5, 12]
        activity_group = ActivityGroupFactory(id=activity_group_ids[0])
        user_activity_group_streak_objs = []
        for i in range(5):
            user_activity_group_streak_objs.append(
                UserActivityGroupStreakFactory(
                    user_id=user_ids[i],
                    activity_group=activity_group,
                    current_streak_count=streak_counts[i],
                    max_streak_count=10,
                ),
            )
        user_activity_group_streak_dtos = []
        for obj in user_activity_group_streak_objs:
            if obj.current_streak_count == streak:
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

        response = storage.get_user_activity_group_streak_for_given_streak(
            activity_group_ids, streak)

        assert response == user_activity_group_streak_dtos

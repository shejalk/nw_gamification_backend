import uuid

import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import ActivityGroupFactory, \
    UserActivityGroupStreakFactory


@pytest.mark.django_db
class TestGetMaxStreakForUserIds:
    @pytest.fixture
    def setup_data(self):
        _ = ActivityGroupFactory.create()
        user_ids = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        streak_count = 0
        user_activity_group_streak_objs = []
        for user_id in user_ids:
            streak_count += 5
            user_activity_group_streak_objs.append(
                UserActivityGroupStreakFactory.create(
                    user_id=user_id,
                    current_streak_count=2,
                    max_streak_count=streak_count,
                ),
            )

        return user_ids, streak_count

    def test_get_max_streak_for_user_ids(self, setup_data):
        user_ids, streak_count = setup_data
        storage = ActivityGroupStorageImplementation()

        expected_response = streak_count

        response = \
            storage.get_max_streak_for_user_ids(user_ids)

        assert response == expected_response

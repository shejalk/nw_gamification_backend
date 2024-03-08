import datetime
import uuid

import pytest

from nw_activities.models import UserActivityGroupStreak
from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import ActivityGroupFactory, \
    UserActivityGroupStreakFactory


@pytest.mark.django_db
class TestUpdateUserActivityGroupStreakLastUpdatedAt:
    @pytest.fixture
    def setup_data(self):
        activity_group = ActivityGroupFactory.create()
        user_id = str(uuid.uuid4())
        _ = (
            UserActivityGroupStreakFactory.create(
                    user_id=user_id,
                    activity_group=activity_group,
                    current_streak_count=2,
                    max_streak_count=10,
                    last_updated_at=datetime.datetime(2022, 8, 1, 9, 0, 0),
                )
        )

        return user_id

    def test_update_user_activity_group_streak_last_updated_at(
            self, setup_data):
        user_id = setup_data
        storage = ActivityGroupStorageImplementation()

        new_last_updated_at = datetime.datetime(2022, 9, 11, 10, 0, 0)

        storage.update_user_activity_group_streak_last_updated_at(
            user_id, new_last_updated_at)

        updated_user_activity_group_streak_object = \
            UserActivityGroupStreak.objects.filter(user_id=user_id)[0]

        assert updated_user_activity_group_streak_object.last_updated_at == \
               new_last_updated_at

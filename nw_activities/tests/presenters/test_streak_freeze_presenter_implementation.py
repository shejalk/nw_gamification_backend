import json
import datetime

from nw_activities.presenters.streak_freeze_presenter_implementation import \
    StreakFreezePresenterImplementation


class TestStreakFreezePresenterImplementation:
    def test_get_streak_freeze_deleted_successfully_response(self, snapshot):
        presenter = StreakFreezePresenterImplementation()

        response = presenter.get_streak_freeze_deleted_successfully_response()

        snapshot.assert_match(response.status_code, "response_status_code")
        snapshot.assert_match(json.loads(response.content), "response_content")

    def test_get_streak_freeze_already_exists_exception(self, snapshot):
        presenter = StreakFreezePresenterImplementation()

        response = presenter.raise_streak_freeze_already_exists_exception(
            datetime.date(2021, 5, 17))

        snapshot.assert_match(response.status_code, "response_status_code")
        snapshot.assert_match(json.loads(response.content), "response_content")

    def test_get_streak_freeze_not_found_exception(self, snapshot):
        presenter = StreakFreezePresenterImplementation()

        response = presenter.raise_streak_freeze_not_found_exception(
            datetime.date(2021, 5, 17))

        snapshot.assert_match(response.status_code, "response_status_code")
        snapshot.assert_match(json.loads(response.content), "response_content")

    def test_get_streak_freeze_created_success_response(self, snapshot):
        presenter = StreakFreezePresenterImplementation()

        response = presenter.get_streak_freeze_created_success_response()

        snapshot.assert_match(response.status_code, "response_status_code")
        snapshot.assert_match(json.loads(response.content), "response_content")

    def test_raise_monthly_freeze_limit_exceeded_exception(self, snapshot):
        presenter = StreakFreezePresenterImplementation()

        response = presenter.raise_monthly_freeze_limit_exceeded_exception(
            1, 2)

        snapshot.assert_match(response.status_code, "response_status_code")
        snapshot.assert_match(json.loads(response.content), "response_content")

    def test_raise_insufficient_streak_freeze_left_exception(self, snapshot):
        presenter = StreakFreezePresenterImplementation()

        response = presenter.raise_insufficient_streak_freeze_left_exception(
            1)

        snapshot.assert_match(response.status_code, "response_status_code")
        snapshot.assert_match(json.loads(response.content), "response_content")

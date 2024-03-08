import datetime

from django_swagger_utils.utils.http_response_mixin import HTTPResponseMixin

from nw_activities.constants.constants import DATE_FORMAT
from nw_activities.interactors.presenter_interfaces. \
    streak_freeze_presenter_interface import StreakFreezePresenterInterface

INSUFFICIENT_FREEZE_BALANCE = (
    "Insufficient freeze balance to freeze streak, balance is {}",
    "INSUFFICIENT_FREEZE_BALANCE",
)

MONTHLY_FREEZE_LIMIT_EXCEEDED = (
    "Monthly freeze limit exceeded, freezes used in current month is {}, "
    "maximum freezes allowed per month is {}",
    "MONTHLY_FREEZE_LIMIT_EXCEEDED",
)

STREAK_FREEZED_SUCCESSFULLY = (
    "Streak freezed successfully",
    "STREAK_FREEZED_SUCCESSFULLY",
)

STREAK_FREEZE_NOT_FOUND = (
    "Streak freeze not found for date {}",
    "STREAK_FREEZE_NOT_FOUND",
)

STREAK_FREEZE_CANCELLED_SUCCESSFULLY = (
    "Streak freeze cancelled successfully",
    "STREAK_FREEZE_CANCELLED_SUCCESSFULLY",
)

STREAK_FREEZE_ALREADY_EXISTS = (
    "Streak freeze already exists for date {}",
    "STREAK_FREEZE_ALREADY_EXISTS",
)


class StreakFreezePresenterImplementation(StreakFreezePresenterInterface,
                                          HTTPResponseMixin):

    def raise_insufficient_streak_freeze_left_exception(
            self, freeze_balance: int):
        response = {
            "response": INSUFFICIENT_FREEZE_BALANCE[0].format(freeze_balance),
            "res_status": INSUFFICIENT_FREEZE_BALANCE[1],
            "http_status_code": 400,
        }

        return self.prepare_400_bad_request_response(response)

    def raise_monthly_freeze_limit_exceeded_exception(
            self, freezes_used_in_current_month: int,
            maximum_freezes_allowed_per_month: int):
        response = {
            "response": MONTHLY_FREEZE_LIMIT_EXCEEDED[0].format(
                freezes_used_in_current_month,
                maximum_freezes_allowed_per_month),
            "res_status": MONTHLY_FREEZE_LIMIT_EXCEEDED[1],
            "http_status_code": 400,
        }

        return self.prepare_400_bad_request_response(response)

    def get_streak_freeze_created_success_response(self):
        response = {
            "response": STREAK_FREEZED_SUCCESSFULLY[0],
            "res_status": STREAK_FREEZED_SUCCESSFULLY[1],
            "http_status_code": 201,
        }

        return self.prepare_201_created_response(response)

    def raise_streak_freeze_not_found_exception(
            self, instance_date: datetime.date):
        datetime_string = instance_date.strftime(DATE_FORMAT)
        response = {
            "response": STREAK_FREEZE_NOT_FOUND[0].format(datetime_string),
            "res_status": STREAK_FREEZE_NOT_FOUND[1],
            "http_status_code": 400,
        }

        return self.prepare_400_bad_request_response(response)

    def get_streak_freeze_deleted_successfully_response(self):
        response = {
            "response": STREAK_FREEZE_CANCELLED_SUCCESSFULLY[0],
            "res_status": STREAK_FREEZE_CANCELLED_SUCCESSFULLY[1],
            "http_status_code": 200,
        }

        return self.prepare_200_success_response(response)

    def raise_streak_freeze_already_exists_exception(
            self, instance_date: datetime.date):
        date_string = instance_date.strftime(DATE_FORMAT)
        response = {
            "response": STREAK_FREEZE_ALREADY_EXISTS[0].format(date_string),
            "res_status": STREAK_FREEZE_ALREADY_EXISTS[1],
            "http_status_code": 400,
        }

        return self.prepare_400_bad_request_response(response)

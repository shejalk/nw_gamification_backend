import abc

import datetime


class StreakFreezePresenterInterface(abc.ABC):

    @abc.abstractmethod
    def get_streak_freeze_created_success_response(self):
        pass

    @abc.abstractmethod
    def raise_insufficient_streak_freeze_left_exception(
            self, freeze_balance: int):
        pass

    @abc.abstractmethod
    def raise_monthly_freeze_limit_exceeded_exception(
            self, freezes_used_in_current_month: int,
            maximum_freezes_allowed_per_month: int):
        pass

    @abc.abstractmethod
    def raise_streak_freeze_not_found_exception(
            self, instance_date: datetime.date):
        pass

    @abc.abstractmethod
    def get_streak_freeze_deleted_successfully_response(self):
        pass

    @abc.abstractmethod
    def raise_streak_freeze_already_exists_exception(
            self, instance_date: datetime.date):
        pass

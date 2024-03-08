import datetime
from typing import Any


class InvalidActivityException(Exception):
    pass


class InvalidInputDataException(Exception):
    def __init__(self, invalid_data: Any):
        self.invalid_data = invalid_data


class InvalidInstanceTypesException(Exception):
    def __init__(self, invalid_instance_types):
        self.invalid_instance_types = invalid_instance_types


class UserDoesNotHaveGamificationAccess(Exception):
    pass


class InsufficientFreezeBalanceException(Exception):
    def __init__(self, freeze_balance: int):
        self.freeze_balance = freeze_balance


class MonthlyFreezeLimitExceededException(Exception):
    def __init__(self, freezes_used_in_current_month: int,
                 maximum_freezes_allowed_per_month: int):
        self.freezes_used_in_current_month = freezes_used_in_current_month
        self.maximum_freezes_allowed_per_month = \
            maximum_freezes_allowed_per_month


class StreakFreezeNotFoundException(Exception):
    pass


class StreakFreezeAlreadyExistsException(Exception):
    def __init__(self, instance_date: datetime.date):
        self.instance_date = instance_date

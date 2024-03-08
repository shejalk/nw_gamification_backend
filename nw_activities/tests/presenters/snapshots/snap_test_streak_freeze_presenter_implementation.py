# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestStreakFreezePresenterImplementation.test_get_streak_freeze_already_exists_exception response_content'] = {
    'http_status_code': 400,
    'res_status': 'STREAK_FREEZE_ALREADY_EXISTS',
    'response': 'Streak freeze already exists for date 2021-05-17'
}

snapshots['TestStreakFreezePresenterImplementation.test_get_streak_freeze_already_exists_exception response_status_code'] = 400

snapshots['TestStreakFreezePresenterImplementation.test_get_streak_freeze_created_success_response response_content'] = {
    'http_status_code': 201,
    'res_status': 'STREAK_FREEZED_SUCCESSFULLY',
    'response': 'Streak freezed successfully'
}

snapshots['TestStreakFreezePresenterImplementation.test_get_streak_freeze_created_success_response response_status_code'] = 201

snapshots['TestStreakFreezePresenterImplementation.test_get_streak_freeze_deleted_successfully_response response_content'] = {
    'http_status_code': 200,
    'res_status': 'STREAK_FREEZE_CANCELLED_SUCCESSFULLY',
    'response': 'Streak freeze cancelled successfully'
}

snapshots['TestStreakFreezePresenterImplementation.test_get_streak_freeze_deleted_successfully_response response_status_code'] = 200

snapshots['TestStreakFreezePresenterImplementation.test_get_streak_freeze_not_found_exception response_content'] = {
    'http_status_code': 400,
    'res_status': 'STREAK_FREEZE_NOT_FOUND',
    'response': 'Streak freeze not found for date 2021-05-17'
}

snapshots['TestStreakFreezePresenterImplementation.test_get_streak_freeze_not_found_exception response_status_code'] = 400

snapshots['TestStreakFreezePresenterImplementation.test_raise_insufficient_streak_freeze_left_exception response_content'] = {
    'http_status_code': 400,
    'res_status': 'INSUFFICIENT_FREEZE_BALANCE',
    'response': 'Insufficient freeze balance to freeze streak, balance is 1'
}

snapshots['TestStreakFreezePresenterImplementation.test_raise_insufficient_streak_freeze_left_exception response_status_code'] = 400

snapshots['TestStreakFreezePresenterImplementation.test_raise_monthly_freeze_limit_exceeded_exception response_content'] = {
    'http_status_code': 400,
    'res_status': 'MONTHLY_FREEZE_LIMIT_EXCEEDED',
    'response': 'Monthly freeze limit exceeded, freezes used in current month is 1, maximum freezes allowed per month is 2'
}

snapshots['TestStreakFreezePresenterImplementation.test_raise_monthly_freeze_limit_exceeded_exception response_status_code'] = 400

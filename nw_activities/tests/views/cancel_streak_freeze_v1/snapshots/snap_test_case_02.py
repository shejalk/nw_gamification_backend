# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCase02CancelStreakFreezeV1APITestCase.test_case body'] = {
    'http_status_code': 400,
    'res_status': 'STREAK_FREEZE_NOT_FOUND',
    'response': 'Streak freeze not found for date 2022-07-15'
}

snapshots['TestCase02CancelStreakFreezeV1APITestCase.test_case status_code'] = '400'

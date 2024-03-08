# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCase01CreateStreakFreezeV1APITestCase.test_case body'] = {
    'http_status_code': 201,
    'res_status': 'STREAK_FREEZED_SUCCESSFULLY',
    'response': 'Streak freezed successfully'
}

snapshots['TestCase01CreateStreakFreezeV1APITestCase.test_case status_code'] = '201'

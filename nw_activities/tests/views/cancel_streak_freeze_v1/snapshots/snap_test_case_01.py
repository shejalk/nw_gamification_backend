# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCase01CancelStreakFreezeV1APITestCase.test_case body'] = {
    'http_status_code': 200,
    'res_status': 'STREAK_FREEZE_CANCELLED_SUCCESSFULLY',
    'response': 'Streak freeze cancelled successfully'
}

snapshots['TestCase01CancelStreakFreezeV1APITestCase.test_case status_code'] = '200'

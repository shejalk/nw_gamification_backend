# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCase02CreateStreakFreezeV1APITestCase.test_case body'] = {
    'http_status_code': 400,
    'res_status': 'MONTHLY_FREEZE_LIMIT_EXCEEDED',
    'response': 'Monthly freeze limit exceeded, freezes used in current month is 4, maximum freezes allowed per month is 3'
}

snapshots['TestCase02CreateStreakFreezeV1APITestCase.test_case status_code'] = '400'

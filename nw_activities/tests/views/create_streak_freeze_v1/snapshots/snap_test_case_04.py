# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCase04CreateStreakFreezeV1APITestCase.test_case body'] = {
    'http_status_code': 400,
    'res_status': 'INSUFFICIENT_FREEZE_BALANCE',
    'response': 'Insufficient freeze balance to freeze streak, balance is 0'
}

snapshots['TestCase04CreateStreakFreezeV1APITestCase.test_case status_code'] = '400'

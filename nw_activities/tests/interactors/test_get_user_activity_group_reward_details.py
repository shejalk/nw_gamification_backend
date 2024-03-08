import uuid

import pytest

from nw_activities.constants.enum import FrequencyTypeEnum, \
    FrequencyPeriodEnum, WeekDayEnum, CompletionStatusEnum
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupFrequencyConfigDTOFactory, \
    UserActivityGroupInstanceDTOFactory, \
    ActivityGroupInstanceIdentifierDTOFactory


class TestGetUserActivityGroupRewardDetailsInteractor:

    @pytest.fixture
    def common_setup(self):
        from unittest.mock import create_autospec
        from nw_activities.interactors.storage_interfaces. \
            activity_group_storage_interface import \
            ActivityGroupStorageInterface
        from nw_activities.interactors.\
            get_user_activity_group_reward_details import \
            GetUserActivityGroupRewardDetailsInteractor

        activity_group_storage_mock = create_autospec(
            ActivityGroupStorageInterface)
        interactor = GetUserActivityGroupRewardDetailsInteractor(
            activity_group_storage_mock)

        return interactor, activity_group_storage_mock

    def test_when_has_not_earned_rewards(self, common_setup):
        _, _ = common_setup

        user_id = str(uuid.uuid4())
        activity_group_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        user_activity_group_instance_ids = [str(uuid.uuid4()),
                                            str(uuid.uuid4())]

        _ = [
            ActivityGroupFrequencyConfigDTOFactory(
                activity_group_id=activity_group_ids[0],
                frequency_type=FrequencyTypeEnum.WEEKLY.value,
                config={
                    "starts_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "09:00:00",
                        },
                        {
                            "value_type": FrequencyPeriodEnum.DAY.value,
                            "value": WeekDayEnum.MONDAY.value,
                        },
                    ],
                    "ends_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "21:00:00",
                        },
                        {
                            "value_type": FrequencyPeriodEnum.DAY.value,
                            "value": WeekDayEnum.SUNDAY.value,
                        },
                    ],
                },
            ),
            ActivityGroupFrequencyConfigDTOFactory(
                activity_group_id=activity_group_ids[1],
                frequency_type=FrequencyTypeEnum.DAILY.value,
                config={
                    "starts_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "07:00:00",
                        },
                    ],
                    "ends_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "23:00:00",
                        },
                    ],
                },
            ),
        ]

        _ = [
            UserActivityGroupInstanceDTOFactory(
                id=user_activity_group_instance_ids[0],
                user_id=user_id,
                activity_group_id=activity_group_ids[0],
                completion_percentage=0.0,
                instance_identifier="2022-07-11 09:00:00#2022-07-17 21:00:00",
                completion_status=CompletionStatusEnum.YET_TO_START.value,
            ),
            UserActivityGroupInstanceDTOFactory(
                id=user_activity_group_instance_ids[1],
                user_id=user_id,
                activity_group_id=activity_group_ids[1],
                completion_percentage=0.0,
                instance_identifier="2022-07-13 07:00:00#2022-07-13 23:00:00",
                completion_status=CompletionStatusEnum.YET_TO_START.value,
            ),
        ]

        _ = [
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=activity_group_ids[0],
                instance_identifier="2022-07-11 09:00:00#2022-07-17 21:00:00",
            ),
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=activity_group_ids[1],
                instance_identifier="2022-07-13 07:00:00#2022-07-13 23:00:00",
            ),
        ]

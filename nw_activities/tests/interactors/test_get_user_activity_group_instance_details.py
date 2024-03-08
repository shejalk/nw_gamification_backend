import datetime
import uuid

import factory
import freezegun
import pytest

from nw_activities.constants.enum import ActivityGroupAssociationTypeEnum, \
    FrequencyTypeEnum, FrequencyPeriodEnum, \
    WeekDayEnum, CompletionStatusEnum, InstanceTypeEnum
from nw_activities.tests.factories.interactor_dtos import \
    UserActivityGroupInstanceWithAssociationDTOFactory, \
    ActivityGroupInstanceDTOFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupAssociationDTOFactory, \
    ActivityGroupFrequencyConfigDTOFactory, \
    UserActivityGroupInstanceDTOFactory, \
    ActivityGroupInstanceIdentifierDTOFactory, \
    UserActivityGroupInstanceWithDatetimeDTOFactory


@freezegun.freeze_time("2022-07-13")
class TestUserActivityGroupInstanceDetails:

    @pytest.fixture
    def common_setup(self):
        from unittest.mock import create_autospec
        from nw_activities.interactors.storage_interfaces. \
            activity_group_storage_interface import \
            ActivityGroupStorageInterface
        from nw_activities.interactors. \
            get_user_activity_group_instance_details import \
            GetUserActivityGroupInstanceInteractor

        activity_group_storage_mock = create_autospec(
            ActivityGroupStorageInterface)
        interactor = GetUserActivityGroupInstanceInteractor(
            activity_group_storage_mock)

        return activity_group_storage_mock, interactor

    @pytest.fixture
    def setup_data_when_user_has_no_activity_group_instances(self):
        weekly_activity_group_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        daily_activity_group_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        user_id = str(uuid.uuid4())

        weekly_activity_group_association_dtos = [
            ActivityGroupAssociationDTOFactory(
                activity_group_id=weekly_activity_group_ids[0],
                association_id=daily_activity_group_ids[0],
                association_type=
                ActivityGroupAssociationTypeEnum.ACTIVITY_GROUP.value,
            ),
            ActivityGroupAssociationDTOFactory(
                activity_group_id=weekly_activity_group_ids[1],
                association_id=daily_activity_group_ids[1],
                association_type=
                ActivityGroupAssociationTypeEnum.ACTIVITY_GROUP.value,
            ),
        ]

        daily_activity_group_association_dtos = [
            ActivityGroupAssociationDTOFactory(
                activity_group_id=daily_activity_group_ids[0],
                association_type=
                ActivityGroupAssociationTypeEnum.ACTIVITY.value,
            ),
            ActivityGroupAssociationDTOFactory(
                activity_group_id=daily_activity_group_ids[1],
                association_type=
                ActivityGroupAssociationTypeEnum.ACTIVITY.value,
            ),
        ]

        activity_group_frequency_config_dtos = [
            ActivityGroupFrequencyConfigDTOFactory(
                activity_group_id=weekly_activity_group_ids[0],
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
                activity_group_id=weekly_activity_group_ids[1],
                frequency_type=FrequencyTypeEnum.WEEKLY.value,
                config={
                    "starts_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "10:00:00",
                        },
                        {
                            "value_type": FrequencyPeriodEnum.DAY.value,
                            "value": WeekDayEnum.MONDAY.value,
                        },
                    ],
                    "ends_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "22:00:00",
                        },
                        {
                            "value_type": FrequencyPeriodEnum.DAY.value,
                            "value": WeekDayEnum.SUNDAY.value,
                        },
                    ],
                },
            ),
            ActivityGroupFrequencyConfigDTOFactory(
                activity_group_id=daily_activity_group_ids[0],
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
            ActivityGroupFrequencyConfigDTOFactory(
                activity_group_id=daily_activity_group_ids[1],
                frequency_type=FrequencyTypeEnum.DAILY.value,
                config={
                    "starts_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "08:00:00",
                        },
                    ],
                    "ends_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "23:59:59",
                        },
                    ],
                },
            ),
        ]

        expected_dtos = [
            UserActivityGroupInstanceWithAssociationDTOFactory(
                user_id=user_id,
                frequency_type=FrequencyTypeEnum.WEEKLY.value,
                activity_group_instance=ActivityGroupInstanceDTOFactory(
                    activity_group_id=weekly_activity_group_ids[0],
                    completion_percentage=0.0,
                    instance_identifier=
                    "2022-07-11 09:00:00#2022-07-17 21:00:00",
                    completion_status=CompletionStatusEnum.YET_TO_START.value,
                    start_datetime=datetime.datetime(2022, 7, 11, 9),
                    end_datetime=datetime.datetime(2022, 7, 17, 21),
                ),
                association_activity_group_instances=
                ActivityGroupInstanceDTOFactory.create_batch(
                    7, activity_group_id=daily_activity_group_ids[0],
                    completion_percentage=0.0,
                    instance_identifier=factory.Iterator([
                        "2022-07-11 07:00:00#2022-07-11 23:00:00",
                        "2022-07-12 07:00:00#2022-07-12 23:00:00",
                        "2022-07-13 07:00:00#2022-07-13 23:00:00",
                        "2022-07-14 07:00:00#2022-07-14 23:00:00",
                        "2022-07-15 07:00:00#2022-07-15 23:00:00",
                        "2022-07-16 07:00:00#2022-07-16 23:00:00",
                        "2022-07-17 07:00:00#2022-07-17 23:00:00",
                    ]),
                    completion_status=CompletionStatusEnum.YET_TO_START.value,
                    start_datetime=factory.Iterator([
                        datetime.datetime(2022, 7, 11, 7),
                        datetime.datetime(2022, 7, 12, 7),
                        datetime.datetime(2022, 7, 13, 7),
                        datetime.datetime(2022, 7, 14, 7),
                        datetime.datetime(2022, 7, 15, 7),
                        datetime.datetime(2022, 7, 16, 7),
                        datetime.datetime(2022, 7, 17, 7),
                    ]),
                    end_datetime=factory.Iterator([
                        datetime.datetime(2022, 7, 11, 23),
                        datetime.datetime(2022, 7, 12, 23),
                        datetime.datetime(2022, 7, 13, 23),
                        datetime.datetime(2022, 7, 14, 23),
                        datetime.datetime(2022, 7, 15, 23),
                        datetime.datetime(2022, 7, 16, 23),
                        datetime.datetime(2022, 7, 17, 23),
                    ]),
                ),
            ),
            UserActivityGroupInstanceWithAssociationDTOFactory(
                user_id=user_id,
                frequency_type=FrequencyTypeEnum.WEEKLY.value,
                activity_group_instance=ActivityGroupInstanceDTOFactory(
                    activity_group_id=weekly_activity_group_ids[1],
                    completion_percentage=0.0,
                    instance_identifier=
                    "2022-07-11 10:00:00#2022-07-17 22:00:00",
                    completion_status=CompletionStatusEnum.YET_TO_START.value,
                    start_datetime=datetime.datetime(2022, 7, 11, 10),
                    end_datetime=datetime.datetime(2022, 7, 17, 22),
                ),
                association_activity_group_instances=
                ActivityGroupInstanceDTOFactory.create_batch(
                    7, activity_group_id=daily_activity_group_ids[1],
                    completion_percentage=0.0,
                    instance_identifier=factory.Iterator([
                        "2022-07-11 08:00:00#2022-07-11 23:59:59",
                        "2022-07-12 08:00:00#2022-07-12 23:59:59",
                        "2022-07-13 08:00:00#2022-07-13 23:59:59",
                        "2022-07-14 08:00:00#2022-07-14 23:59:59",
                        "2022-07-15 08:00:00#2022-07-15 23:59:59",
                        "2022-07-16 08:00:00#2022-07-16 23:59:59",
                        "2022-07-17 08:00:00#2022-07-17 23:59:59",
                    ]),
                    completion_status=CompletionStatusEnum.YET_TO_START.value,
                    start_datetime=factory.Iterator([
                        datetime.datetime(2022, 7, 11, 8),
                        datetime.datetime(2022, 7, 12, 8),
                        datetime.datetime(2022, 7, 13, 8),
                        datetime.datetime(2022, 7, 14, 8),
                        datetime.datetime(2022, 7, 15, 8),
                        datetime.datetime(2022, 7, 16, 8),
                        datetime.datetime(2022, 7, 17, 8),
                    ]),
                    end_datetime=factory.Iterator([
                        datetime.datetime(2022, 7, 11, 23, 59, 59),
                        datetime.datetime(2022, 7, 12, 23, 59, 59),
                        datetime.datetime(2022, 7, 13, 23, 59, 59),
                        datetime.datetime(2022, 7, 14, 23, 59, 59),
                        datetime.datetime(2022, 7, 15, 23, 59, 59),
                        datetime.datetime(2022, 7, 16, 23, 59, 59),
                        datetime.datetime(2022, 7, 17, 23, 59, 59),
                    ]),
                ),
            ),
            UserActivityGroupInstanceWithAssociationDTOFactory(
                user_id=user_id,
                frequency_type=FrequencyTypeEnum.DAILY.value,
                activity_group_instance=ActivityGroupInstanceDTOFactory(
                    activity_group_id=daily_activity_group_ids[0],
                    completion_percentage=0.0,
                    instance_identifier=
                    "2022-07-13 07:00:00#2022-07-13 23:00:00",
                    completion_status=CompletionStatusEnum.YET_TO_START.value,
                    start_datetime=datetime.datetime(2022, 7, 13, 7),
                    end_datetime=datetime.datetime(2022, 7, 13, 23),
                ),
                association_activity_group_instances=[],
            ),
            UserActivityGroupInstanceWithAssociationDTOFactory(
                user_id=user_id,
                frequency_type=FrequencyTypeEnum.DAILY.value,
                activity_group_instance=ActivityGroupInstanceDTOFactory(
                    activity_group_id=daily_activity_group_ids[1],
                    completion_percentage=0.0,
                    instance_identifier=
                    "2022-07-13 08:00:00#2022-07-13 23:59:59",
                    completion_status=CompletionStatusEnum.YET_TO_START.value,
                    start_datetime=datetime.datetime(2022, 7, 13, 8),
                    end_datetime=datetime.datetime(2022, 7, 13, 23, 59, 59),
                ),
                association_activity_group_instances=[],
            ),
        ]

        return weekly_activity_group_ids, daily_activity_group_ids, \
            weekly_activity_group_association_dtos, \
            daily_activity_group_association_dtos, \
            activity_group_frequency_config_dtos, user_id, expected_dtos

    def test_when_user_has_no_activity_group_instances(
            self, common_setup,
            setup_data_when_user_has_no_activity_group_instances):
        activity_group_storage_mock, interactor = common_setup

        weekly_activity_group_ids, daily_activity_group_ids, \
            weekly_activity_group_association_dtos, \
            daily_activity_group_association_dtos, \
            activity_group_frequency_config_dtos, user_id, expected_dtos = \
            setup_data_when_user_has_no_activity_group_instances

        activity_group_ids = weekly_activity_group_ids + \
            daily_activity_group_ids
        activity_group_association_dtos = \
            weekly_activity_group_association_dtos + \
            daily_activity_group_association_dtos

        activity_group_storage_mock.get_all_activity_group_ids.return_value =\
            activity_group_ids
        activity_group_storage_mock \
            .get_activity_group_associations_for_activity_group_ids.\
            return_value = activity_group_association_dtos
        activity_group_storage_mock.get_user_activity_group_instances \
            .return_value = []
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos

        response = interactor.get_user_activity_group_instances(user_id)

        assert len(response) == len(expected_dtos)
        for dto in expected_dtos:
            assert dto in response

        call_args = \
            activity_group_storage_mock.get_activity_groups_frequency_configs \
                .call_args_list
        for activity_group_id in activity_group_ids:
            assert activity_group_id in call_args[0][0][0]

    @pytest.fixture
    def setup_data_when_user_has_activity_group_instances(self):
        weekly_activity_group_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        daily_activity_group_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        user_id = str(uuid.uuid4())

        weekly_activity_group_association_dtos = [
            ActivityGroupAssociationDTOFactory(
                activity_group_id=weekly_activity_group_ids[0],
                association_id=daily_activity_group_ids[0],
                association_type=
                ActivityGroupAssociationTypeEnum.ACTIVITY_GROUP.value,
            ),
            ActivityGroupAssociationDTOFactory(
                activity_group_id=weekly_activity_group_ids[1],
                association_id=daily_activity_group_ids[1],
                association_type=
                ActivityGroupAssociationTypeEnum.ACTIVITY_GROUP.value,
            ),
        ]

        daily_activity_group_association_dtos = [
            ActivityGroupAssociationDTOFactory(
                activity_group_id=daily_activity_group_ids[0],
                association_type=
                ActivityGroupAssociationTypeEnum.ACTIVITY.value,
            ),
            ActivityGroupAssociationDTOFactory(
                activity_group_id=daily_activity_group_ids[1],
                association_type=
                ActivityGroupAssociationTypeEnum.ACTIVITY.value,
            ),
        ]

        activity_group_frequency_config_dtos = [
            ActivityGroupFrequencyConfigDTOFactory(
                activity_group_id=weekly_activity_group_ids[0],
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
                activity_group_id=weekly_activity_group_ids[1],
                frequency_type=FrequencyTypeEnum.WEEKLY.value,
                config={
                    "starts_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "10:00:00",
                        },
                        {
                            "value_type": FrequencyPeriodEnum.DAY.value,
                            "value": WeekDayEnum.MONDAY.value,
                        },
                    ],
                    "ends_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "22:00:00",
                        },
                        {
                            "value_type": FrequencyPeriodEnum.DAY.value,
                            "value": WeekDayEnum.SUNDAY.value,
                        },
                    ],
                },
            ),
            ActivityGroupFrequencyConfigDTOFactory(
                activity_group_id=daily_activity_group_ids[0],
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
            ActivityGroupFrequencyConfigDTOFactory(
                activity_group_id=daily_activity_group_ids[1],
                frequency_type=FrequencyTypeEnum.DAILY.value,
                config={
                    "starts_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "08:00:00",
                        },
                    ],
                    "ends_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "23:59:59",
                        },
                    ],
                },
            ),
        ]

        user_activity_group_instance_dtos = [
            UserActivityGroupInstanceDTOFactory(
                user_id=user_id,
                activity_group_id=weekly_activity_group_ids[0],
                completion_percentage=50.0,
                instance_identifier="2022-07-11 09:00:00#2022-07-17 21:00:00",
                completion_status=CompletionStatusEnum.IN_PROGRESS.value,
            ),
            UserActivityGroupInstanceDTOFactory(
                user_id=user_id,
                activity_group_id=weekly_activity_group_ids[1],
                completion_percentage=60.0,
                instance_identifier="2022-07-11 10:00:00#2022-07-17 22:00:00",
                completion_status=CompletionStatusEnum.IN_PROGRESS.value,
            ),
            UserActivityGroupInstanceDTOFactory(
                user_id=user_id,
                activity_group_id=daily_activity_group_ids[0],
                completion_percentage=100.0,
                instance_identifier="2022-07-11 07:00:00#2022-07-11 23:00:00",
                completion_status=CompletionStatusEnum.COMPLETED.value,
            ),
            UserActivityGroupInstanceDTOFactory(
                user_id=user_id,
                activity_group_id=daily_activity_group_ids[0],
                completion_percentage=100.0,
                instance_identifier="2022-07-12 07:00:00#2022-07-12 23:00:00",
                completion_status=CompletionStatusEnum.COMPLETED.value,
            ),
            UserActivityGroupInstanceDTOFactory(
                user_id=user_id,
                activity_group_id=daily_activity_group_ids[0],
                completion_percentage=20.0,
                instance_identifier="2022-07-13 07:00:00#2022-07-13 23:00:00",
                completion_status=CompletionStatusEnum.IN_PROGRESS.value,
            ),
            UserActivityGroupInstanceDTOFactory(
                user_id=user_id,
                activity_group_id=daily_activity_group_ids[1],
                completion_percentage=100.0,
                instance_identifier="2022-07-11 08:00:00#2022-07-11 23:59:59",
                completion_status=CompletionStatusEnum.COMPLETED.value,
            ),
            UserActivityGroupInstanceDTOFactory(
                user_id=user_id,
                activity_group_id=daily_activity_group_ids[1],
                completion_percentage=50.0,
                instance_identifier="2022-07-12 08:00:00#2022-07-12 23:59:59",
                completion_status=CompletionStatusEnum.IN_PROGRESS.value,
            ),
            UserActivityGroupInstanceDTOFactory(
                user_id=user_id,
                activity_group_id=daily_activity_group_ids[1],
                completion_percentage=30.0,
                instance_identifier="2022-07-13 08:00:00#2022-07-13 23:59:59",
                completion_status=CompletionStatusEnum.IN_PROGRESS.value,
            ),
        ]

        expected_dtos = [
            UserActivityGroupInstanceWithAssociationDTOFactory(
                user_id=user_id,
                frequency_type=FrequencyTypeEnum.WEEKLY.value,
                activity_group_instance=ActivityGroupInstanceDTOFactory(
                    activity_group_id=weekly_activity_group_ids[0],
                    completion_percentage=50.0,
                    instance_identifier=
                    "2022-07-11 09:00:00#2022-07-17 21:00:00",
                    completion_status=CompletionStatusEnum.IN_PROGRESS.value,
                    start_datetime=datetime.datetime(2022, 7, 11, 9),
                    end_datetime=datetime.datetime(2022, 7, 17, 21),
                ),
                association_activity_group_instances=
                ActivityGroupInstanceDTOFactory.create_batch(
                    7, activity_group_id=daily_activity_group_ids[0],
                    completion_percentage=factory.Iterator(
                        [100.0, 100.0, 20.0, 0.0, 0.0, 0.0, 0.0],
                    ),
                    instance_identifier=factory.Iterator([
                        "2022-07-11 07:00:00#2022-07-11 23:00:00",
                        "2022-07-12 07:00:00#2022-07-12 23:00:00",
                        "2022-07-13 07:00:00#2022-07-13 23:00:00",
                        "2022-07-14 07:00:00#2022-07-14 23:00:00",
                        "2022-07-15 07:00:00#2022-07-15 23:00:00",
                        "2022-07-16 07:00:00#2022-07-16 23:00:00",
                        "2022-07-17 07:00:00#2022-07-17 23:00:00",
                    ]),
                    completion_status=factory.Iterator(
                        [
                            CompletionStatusEnum.COMPLETED.value,
                            CompletionStatusEnum.COMPLETED.value,
                            CompletionStatusEnum.IN_PROGRESS.value,
                            CompletionStatusEnum.YET_TO_START.value,
                            CompletionStatusEnum.YET_TO_START.value,
                            CompletionStatusEnum.YET_TO_START.value,
                            CompletionStatusEnum.YET_TO_START.value,
                        ],
                    ),
                    start_datetime=factory.Iterator([
                        datetime.datetime(2022, 7, 11, 7),
                        datetime.datetime(2022, 7, 12, 7),
                        datetime.datetime(2022, 7, 13, 7),
                        datetime.datetime(2022, 7, 14, 7),
                        datetime.datetime(2022, 7, 15, 7),
                        datetime.datetime(2022, 7, 16, 7),
                        datetime.datetime(2022, 7, 17, 7),
                    ]),
                    end_datetime=factory.Iterator([
                        datetime.datetime(2022, 7, 11, 23),
                        datetime.datetime(2022, 7, 12, 23),
                        datetime.datetime(2022, 7, 13, 23),
                        datetime.datetime(2022, 7, 14, 23),
                        datetime.datetime(2022, 7, 15, 23),
                        datetime.datetime(2022, 7, 16, 23),
                        datetime.datetime(2022, 7, 17, 23),
                    ]),
                ),
            ),
            UserActivityGroupInstanceWithAssociationDTOFactory(
                user_id=user_id,
                frequency_type=FrequencyTypeEnum.WEEKLY.value,
                activity_group_instance=ActivityGroupInstanceDTOFactory(
                    activity_group_id=weekly_activity_group_ids[1],
                    completion_percentage=60.0,
                    instance_identifier=
                    "2022-07-11 10:00:00#2022-07-17 22:00:00",
                    completion_status=CompletionStatusEnum.IN_PROGRESS.value,
                    start_datetime=datetime.datetime(2022, 7, 11, 10),
                    end_datetime=datetime.datetime(2022, 7, 17, 22),
                ),
                association_activity_group_instances=
                ActivityGroupInstanceDTOFactory.create_batch(
                    7, activity_group_id=daily_activity_group_ids[1],
                    completion_percentage=factory.Iterator(
                        [100.0, 50.0, 30.0, 0.0, 0.0, 0.0, 0.0],
                    ),
                    instance_identifier=factory.Iterator([
                        "2022-07-11 08:00:00#2022-07-11 23:59:59",
                        "2022-07-12 08:00:00#2022-07-12 23:59:59",
                        "2022-07-13 08:00:00#2022-07-13 23:59:59",
                        "2022-07-14 08:00:00#2022-07-14 23:59:59",
                        "2022-07-15 08:00:00#2022-07-15 23:59:59",
                        "2022-07-16 08:00:00#2022-07-16 23:59:59",
                        "2022-07-17 08:00:00#2022-07-17 23:59:59",
                    ]),
                    completion_status=factory.Iterator(
                        [
                            CompletionStatusEnum.COMPLETED.value,
                            CompletionStatusEnum.IN_PROGRESS.value,
                            CompletionStatusEnum.IN_PROGRESS.value,
                            CompletionStatusEnum.YET_TO_START.value,
                            CompletionStatusEnum.YET_TO_START.value,
                            CompletionStatusEnum.YET_TO_START.value,
                            CompletionStatusEnum.YET_TO_START.value,
                        ],
                    ),
                    start_datetime=factory.Iterator([
                        datetime.datetime(2022, 7, 11, 8),
                        datetime.datetime(2022, 7, 12, 8),
                        datetime.datetime(2022, 7, 13, 8),
                        datetime.datetime(2022, 7, 14, 8),
                        datetime.datetime(2022, 7, 15, 8),
                        datetime.datetime(2022, 7, 16, 8),
                        datetime.datetime(2022, 7, 17, 8),
                    ]),
                    end_datetime=factory.Iterator([
                        datetime.datetime(2022, 7, 11, 23, 59, 59),
                        datetime.datetime(2022, 7, 12, 23, 59, 59),
                        datetime.datetime(2022, 7, 13, 23, 59, 59),
                        datetime.datetime(2022, 7, 14, 23, 59, 59),
                        datetime.datetime(2022, 7, 15, 23, 59, 59),
                        datetime.datetime(2022, 7, 16, 23, 59, 59),
                        datetime.datetime(2022, 7, 17, 23, 59, 59),
                    ]),
                ),
            ),
            UserActivityGroupInstanceWithAssociationDTOFactory(
                user_id=user_id,
                frequency_type=FrequencyTypeEnum.DAILY.value,
                activity_group_instance=ActivityGroupInstanceDTOFactory(
                    activity_group_id=daily_activity_group_ids[0],
                    completion_percentage=20.0,
                    instance_identifier=
                    "2022-07-13 07:00:00#2022-07-13 23:00:00",
                    completion_status=CompletionStatusEnum.IN_PROGRESS.value,
                    start_datetime=datetime.datetime(2022, 7, 13, 7),
                    end_datetime=datetime.datetime(2022, 7, 13, 23),
                ),
                association_activity_group_instances=[],
            ),
            UserActivityGroupInstanceWithAssociationDTOFactory(
                user_id=user_id,
                frequency_type=FrequencyTypeEnum.DAILY.value,
                activity_group_instance=ActivityGroupInstanceDTOFactory(
                    activity_group_id=daily_activity_group_ids[1],
                    completion_percentage=30.0,
                    instance_identifier=
                    "2022-07-13 08:00:00#2022-07-13 23:59:59",
                    completion_status=CompletionStatusEnum.IN_PROGRESS.value,
                    start_datetime=datetime.datetime(2022, 7, 13, 8),
                    end_datetime=datetime.datetime(2022, 7, 13, 23, 59, 59),
                ),
                association_activity_group_instances=[],
            ),
        ]

        return weekly_activity_group_ids, daily_activity_group_ids, \
            weekly_activity_group_association_dtos, \
            daily_activity_group_association_dtos, \
            activity_group_frequency_config_dtos, user_id, expected_dtos, \
            user_activity_group_instance_dtos

    @pytest.fixture
    def setup_data_when_user_has_activity_group_instances_for_multiple_dates(
            self):
        activity_group_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        user_id = str(uuid.uuid4())

        activity_group_frequency_config_dtos = [
            ActivityGroupFrequencyConfigDTOFactory(
                activity_group_id=activity_group_ids[0],
                frequency_type=FrequencyTypeEnum.WEEKLY.value,
                config={
                    "starts_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "10:00:00",
                        },
                        {
                            "value_type": FrequencyPeriodEnum.DAY.value,
                            "value": WeekDayEnum.MONDAY.value,
                        },
                    ],
                    "ends_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "22:00:00",
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

        user_activity_group_instance_dtos = [
            UserActivityGroupInstanceDTOFactory(
                user_id=user_id,
                activity_group_id=activity_group_ids[0],
                completion_percentage=50.0,
                instance_identifier="2022-07-11 09:00:00#2022-07-17 21:00:00",
                completion_status=CompletionStatusEnum.IN_PROGRESS.value,
                instance_type=InstanceTypeEnum.FREEZE.value,
            ),
            UserActivityGroupInstanceDTOFactory(
                user_id=user_id,
                activity_group_id=activity_group_ids[1],
                completion_percentage=100.0,
                instance_identifier="2022-07-11 08:00:00#2022-07-11 23:59:59",
                completion_status=CompletionStatusEnum.COMPLETED.value,
                instance_type=InstanceTypeEnum.FREEZE.value,
            ),
        ]

        expected_dtos = [
            UserActivityGroupInstanceWithDatetimeDTOFactory(
                id=each.id,
                user_id=each.user_id,
                activity_group_id=each.activity_group_id,
                completion_percentage=each.completion_percentage,
                instance_identifier=each.instance_identifier,
                completion_status=each.completion_status,
                instance_type=each.instance_type,
            )
            for each in user_activity_group_instance_dtos
        ]
        expected_dtos[0].start_datetime = datetime.datetime(2022, 7, 11, 9)
        expected_dtos[0].end_datetime = datetime.datetime(2022, 7, 17, 21)
        expected_dtos[1].start_datetime = datetime.datetime(2022, 7, 11, 8)
        expected_dtos[1].end_datetime = datetime.datetime(2022, 7, 11, 23, 59,
                                                          59)

        return activity_group_ids, activity_group_frequency_config_dtos, \
            user_id, expected_dtos, user_activity_group_instance_dtos

    def test_when_user_has_activity_group_instances(
            self, common_setup,
            setup_data_when_user_has_activity_group_instances):
        activity_group_storage_mock, interactor = common_setup

        weekly_activity_group_ids, daily_activity_group_ids, \
            weekly_activity_group_association_dtos, \
            daily_activity_group_association_dtos, \
            activity_group_frequency_config_dtos, user_id, expected_dtos, \
            user_activity_group_instance_dtos = \
            setup_data_when_user_has_activity_group_instances

        activity_group_ids = weekly_activity_group_ids + \
            daily_activity_group_ids
        activity_group_association_dtos = \
            weekly_activity_group_association_dtos + \
            daily_activity_group_association_dtos

        activity_group_storage_mock.get_all_activity_group_ids.return_value = \
            activity_group_ids
        activity_group_storage_mock \
            .get_activity_group_associations_for_activity_group_ids. \
            return_value = activity_group_association_dtos
        activity_group_storage_mock.get_user_activity_group_instances \
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos

        response = interactor.get_user_activity_group_instances(user_id)

        assert len(response) == len(expected_dtos)
        for dto in expected_dtos:
            assert dto in response

        call_args = \
            activity_group_storage_mock.get_activity_groups_frequency_configs\
            .call_args_list
        for activity_group_id in activity_group_ids:
            assert activity_group_id in call_args[0][0][0]

    def test_get_agi_user_ids_for_instance_and_frequency_type(
            self, common_setup):
        activity_group_storage_mock, interactor = common_setup
        activity_group_ids = [str(uuid.uuid4()), str(uuid.uuid4()),
                              str(uuid.uuid4()), str(uuid.uuid4())]
        instance_identifiers = [
            "2022-07-13 07:00:00#2022-07-13 23:00:00",
            "2022-07-13 08:00:00#2022-07-13 23:59:59",
        ]
        instance_type = InstanceTypeEnum.LEISURE.value
        frequency_type = FrequencyTypeEnum.DAILY.value
        user_ids = [str(uuid.uuid4()), str(uuid.uuid4())]

        activity_group_frequency_config_dtos = [
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
                frequency_type=FrequencyTypeEnum.WEEKLY.value,
                config={
                    "starts_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "10:00:00",
                        },
                        {
                            "value_type": FrequencyPeriodEnum.DAY.value,
                            "value": WeekDayEnum.MONDAY.value,
                        },
                    ],
                    "ends_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "22:00:00",
                        },
                        {
                            "value_type": FrequencyPeriodEnum.DAY.value,
                            "value": WeekDayEnum.SUNDAY.value,
                        },
                    ],
                },
            ),
            ActivityGroupFrequencyConfigDTOFactory(
                activity_group_id=activity_group_ids[2],
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
            ActivityGroupFrequencyConfigDTOFactory(
                activity_group_id=activity_group_ids[3],
                frequency_type=FrequencyTypeEnum.DAILY.value,
                config={
                    "starts_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "08:00:00",
                        },
                    ],
                    "ends_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "23:59:59",
                        },
                    ],
                },
            ),
        ]

        activity_group_instance_identifier_dtos = [
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=activity_group_ids[2],
                instance_identifier=instance_identifiers[0],
            ),
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=activity_group_ids[3],
                instance_identifier=instance_identifiers[1],
            ),
        ]

        activity_group_storage_mock.get_all_activity_group_ids.return_value =\
            activity_group_ids
        activity_group_storage_mock.get_streak_enabled_activity_group_ids\
            .return_value = []
        activity_group_storage_mock.get_activity_groups_frequency_configs\
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock\
            .get_activity_group_instance_user_ids_for_instance_type\
            .return_value = user_ids

        response = interactor.get_agi_user_ids_for_instance_and_frequency_type(
            instance_type, frequency_type)

        assert len(user_ids) == len(response)
        assert user_ids == response

        activity_group_storage_mock.get_all_activity_group_ids\
            .assert_called_once()
        actual_activity_group_ids = \
            activity_group_storage_mock.get_activity_groups_frequency_configs\
            .call_args
        for each in activity_group_ids:
            assert each in actual_activity_group_ids[0][0]

        activity_group_storage_mock \
            .get_activity_group_instance_user_ids_for_instance_type \
            .assert_called_once_with(
            activity_group_instance_identifier_dtos, instance_type)

    def test_for_given_dates_when_user_has_activity_group_instances(
            self, common_setup,
            setup_data_when_user_has_activity_group_instances_for_multiple_dates):
        # Arrange
        activity_group_storage_mock, interactor = common_setup
        activity_group_ids, activity_group_frequency_config_dtos, \
            user_id, expected_dtos, user_activity_group_instance_dtos = \
            setup_data_when_user_has_activity_group_instances_for_multiple_dates

        activity_group_storage_mock.get_streak_enabled_activity_group_ids.return_value = \
            activity_group_ids
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock \
            .get_user_activity_group_instances_of_given_types \
            .return_value = user_activity_group_instance_dtos
        instance_dates = [
            datetime.datetime(2022, 7, 13, 7),
            datetime.datetime(2022, 7, 12, 8),
        ]
        instance_identifiers = [
            "2022-07-11 10:00:00#2022-07-17 22:00:00",
            "2022-07-13 07:00:00#2022-07-13 23:00:00",
            "2022-07-11 10:00:00#2022-07-17 22:00:00",
            "2022-07-12 07:00:00#2022-07-12 23:00:00",
        ]
        activity_group_identifiers = [
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=activity_group_ids[each % 2],
                instance_identifier=instance_identifiers[each],
            )
            for each in range(4)
        ]
        instance_types = [InstanceTypeEnum.FREEZE.value]

        # Act
        response = interactor. \
            get_user_streak_activity_group_instances_for_given_dates(
                user_id, instance_dates, instance_types)

        # Assert
        assert len(response) == len(expected_dtos)
        for dto in expected_dtos:
            assert dto in response

        activity_group_storage_mock.get_streak_enabled_activity_group_ids \
            .assert_called_once_with()
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock \
            .get_user_activity_group_instances_of_given_types \
            .assert_called_once_with(
            user_id, activity_group_identifiers, instance_types)

    def test_between_dates_when_user_has_activity_group_instances(
            self, common_setup,
            setup_data_when_user_has_activity_group_instances_for_multiple_dates):
        # Arrange
        activity_group_storage_mock, interactor = common_setup
        activity_group_ids, activity_group_frequency_config_dtos, \
            user_id, expected_dtos, user_activity_group_instance_dtos = \
            setup_data_when_user_has_activity_group_instances_for_multiple_dates

        activity_group_storage_mock.get_streak_enabled_activity_group_ids.return_value = \
            activity_group_ids
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock \
            .get_user_activity_group_instances_of_given_types \
            .return_value = user_activity_group_instance_dtos
        instance_dates = [
            datetime.date(2022, 7, 11),
            datetime.date(2022, 7, 13),
        ]
        instance_identifiers = [
            "2022-07-11 10:00:00#2022-07-17 22:00:00",
            "2022-07-11 07:00:00#2022-07-11 23:00:00",
            "2022-07-11 10:00:00#2022-07-17 22:00:00",
            "2022-07-12 07:00:00#2022-07-12 23:00:00",
            "2022-07-11 10:00:00#2022-07-17 22:00:00",
            "2022-07-13 07:00:00#2022-07-13 23:00:00",
        ]
        activity_group_identifiers = [
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=activity_group_ids[each % 2],
                instance_identifier=instance_identifiers[each],
            )
            for each in range(6)
        ]
        instance_types = [InstanceTypeEnum.FREEZE.value]

        # Act
        response = interactor. \
            get_user_streak_activity_group_instances_between_given_dates(
            user_id, instance_dates[0], instance_dates[1], instance_types)

        # Assert
        assert len(response) == len(expected_dtos)
        for dto in expected_dtos:
            assert dto in response

        activity_group_storage_mock.get_streak_enabled_activity_group_ids \
            .assert_called_once_with()
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock \
            .get_user_activity_group_instances_of_given_types \
            .assert_called_once_with(
            user_id, activity_group_identifiers, instance_types)

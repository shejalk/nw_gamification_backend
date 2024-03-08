import uuid

import freezegun
import pytest

from nw_activities.constants.enum import FrequencyTypeEnum, \
    FrequencyPeriodEnum, WeekDayEnum, CompletionStatusEnum, \
    CompletionMetricEntityTypeEnum
from nw_activities.tests.factories.interactor_dtos import \
    UserActivityGroupCompletionMetricDTOFactory, UserCompletionMetricDTOFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupFrequencyConfigDTOFactory, \
    UserActivityGroupInstanceDTOFactory, \
    ActivityGroupInstanceIdentifierDTOFactory, \
    ActivityGroupCompletionMetricDTOFactory, \
    ActivityGroupInstanceCountDTOFactory, \
    UserActivityGroupInstanceMetricTrackerDTOFactory


@freezegun.freeze_time("2022-07-13")
class TestGetActivityGroupInstanceCompletionMetrics:

    @pytest.fixture
    def common_setup(self):
        from nw_activities.interactors.\
            get_activity_group_instance_completion_metrics \
            import GetActivityGroupInstanceCompletionMetricInteractor
        from unittest.mock import create_autospec
        from nw_activities.interactors.storage_interfaces.\
            activity_group_storage_interface import \
            ActivityGroupStorageInterface

        activity_group_storage_mock = create_autospec(
            ActivityGroupStorageInterface)
        interactor = GetActivityGroupInstanceCompletionMetricInteractor(
            activity_group_storage_mock)

        return interactor, activity_group_storage_mock

    @pytest.fixture()
    def empty_user_activity_group_instance_metric_trackers_setup(self):
        user_id = str(uuid.uuid4())
        activity_group_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        entity_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        completion_metric_target_values = [10.0, 20.0]
        entity_types = [CompletionMetricEntityTypeEnum.RESOURCE.value,
                        CompletionMetricEntityTypeEnum.
                        ACTIVITY_GROUP_ASSOCIATION.value]
        user_activity_group_instance_ids = [str(uuid.uuid4()),
                                            str(uuid.uuid4())]
        activity_group_instances_count = [4, 8]

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

        activity_group_instance_identifier_dtos = [
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=activity_group_ids[0],
                instance_identifier="2022-07-11 09:00:00#2022-07-17 21:00:00",
            ),
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=activity_group_ids[1],
                instance_identifier="2022-07-13 07:00:00#2022-07-13 23:00:00",
            ),
        ]

        activity_group_completion_metric_dtos = [
            ActivityGroupCompletionMetricDTOFactory(
                entity_id=entity_ids[0],
                activity_group_id=activity_group_ids[0],
                value=completion_metric_target_values[0],
                entity_type=entity_types[0],
            ),
            ActivityGroupCompletionMetricDTOFactory(
                entity_id=entity_ids[1],
                activity_group_id=activity_group_ids[1],
                value=completion_metric_target_values[1],
                entity_type=entity_types[1],
            ),
        ]

        activity_group_instances_count_dtos = [
            ActivityGroupInstanceCountDTOFactory(
                activity_group_id=activity_group_ids[0],
                activity_group_instances_count=
                activity_group_instances_count[0],
            ),
            ActivityGroupInstanceCountDTOFactory(
                activity_group_id=activity_group_ids[1],
                activity_group_instances_count=
                activity_group_instances_count[1],
            ),
        ]

        user_activity_group_instance_metric_tracker_dtos = []

        expected_user_activity_group_instance_with_association_dtos = [
            UserActivityGroupCompletionMetricDTOFactory(
                activity_group_id=activity_group_ids[0],
                no_of_activity_group_instances_completed
                =activity_group_instances_count[0],
                instance_completion_metrics=[
                    UserCompletionMetricDTOFactory(
                        target_value=completion_metric_target_values[0],
                        current_value=0,
                        entity_id=entity_ids[0],
                        entity_type=entity_types[0],
                    ),
                ],
            ),
            UserActivityGroupCompletionMetricDTOFactory(
                activity_group_id=activity_group_ids[1],
                no_of_activity_group_instances_completed
                =activity_group_instances_count[1],
                instance_completion_metrics=[
                    UserCompletionMetricDTOFactory(
                        target_value=completion_metric_target_values[1],
                        current_value=0,
                        entity_id=entity_ids[1],
                        entity_type=entity_types[1],
                    ),
                ],
            ),
        ]

        return activity_group_completion_metric_dtos, \
            activity_group_frequency_config_dtos, activity_group_ids, \
            activity_group_instance_identifier_dtos, \
            activity_group_instances_count_dtos, \
            expected_user_activity_group_instance_with_association_dtos, \
            user_activity_group_instance_dtos, \
            user_activity_group_instance_ids,\
            user_activity_group_instance_metric_tracker_dtos, user_id

    def test_when_user_activity_group_instance_metrics_are_empty(
            self, common_setup,
            empty_user_activity_group_instance_metric_trackers_setup):
        interactor, activity_group_storage_mock = common_setup
        activity_group_completion_metric_dtos, \
            activity_group_frequency_config_dtos, \
            activity_group_ids, activity_group_instance_identifier_dtos, \
            activity_group_instances_count_dtos, \
            expected_user_activity_group_instance_with_association_dtos, \
            user_activity_group_instance_dtos, \
            user_activity_group_instance_ids, \
            user_activity_group_instance_metric_tracker_dtos, user_id = \
            empty_user_activity_group_instance_metric_trackers_setup

        activity_group_storage_mock.get_activity_groups_frequency_configs\
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_user_activity_group_instances\
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_activity_groups_completion_metrics\
            .return_value = activity_group_completion_metric_dtos
        activity_group_storage_mock\
            .get_user_activity_group_instances_metric_tracker_without_transaction.return_value = \
            user_activity_group_instance_metric_tracker_dtos
        activity_group_storage_mock\
            .get_activity_group_instances_count_for_completion_status\
            .return_value = activity_group_instances_count_dtos

        actual_user_activity_group_instance_with_association_dtos = \
            interactor.get_activity_group_instance_completion_metrics(
                user_id, activity_group_ids)

        assert expected_user_activity_group_instance_with_association_dtos == \
               actual_user_activity_group_instance_with_association_dtos

        activity_group_storage_mock.get_activity_groups_frequency_configs\
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_user_activity_group_instances \
            .assert_called_once_with(user_id,
                                     activity_group_instance_identifier_dtos)
        activity_group_storage_mock.get_activity_groups_completion_metrics\
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock\
            .get_user_activity_group_instances_metric_tracker_without_transaction\
            .assert_called_once_with(user_activity_group_instance_ids)
        activity_group_storage_mock \
            .get_activity_group_instances_count_for_completion_status\
            .assert_called_once_with(user_id, activity_group_ids,
                                     CompletionStatusEnum.COMPLETED.value)

    @pytest.fixture
    def user_activity_group_instance_metric_trackers_setup(self):
        user_id = str(uuid.uuid4())
        activity_group_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        entity_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        completion_metric_target_values = [10.0, 20.0]
        entity_types = [CompletionMetricEntityTypeEnum.RESOURCE.value,
                        CompletionMetricEntityTypeEnum.
                        ACTIVITY_GROUP_ASSOCIATION.value]
        user_activity_group_instance_ids = [str(uuid.uuid4()),
                                            str(uuid.uuid4())]
        activity_group_instances_count = [4, 8]
        activity_group_completion_metric_ids = \
            [str(uuid.uuid4()), str(uuid.uuid4())]
        activity_group_completion_metric_current_value = \
            [10, 10]

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
                id=user_activity_group_instance_ids[0],
                user_id=user_id,
                activity_group_id=activity_group_ids[0],
                completion_percentage=100.0,
                instance_identifier="2022-07-11 09:00:00#2022-07-17 21:00:00",
                completion_status=CompletionStatusEnum.COMPLETED.value,
            ),
            UserActivityGroupInstanceDTOFactory(
                id=user_activity_group_instance_ids[1],
                user_id=user_id,
                activity_group_id=activity_group_ids[1],
                completion_percentage=50.0,
                instance_identifier="2022-07-13 07:00:00#2022-07-13 23:00:00",
                completion_status=CompletionStatusEnum.IN_PROGRESS.value,
            ),
        ]

        activity_group_instance_identifier_dtos = [
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=activity_group_ids[0],
                instance_identifier="2022-07-11 09:00:00#2022-07-17 21:00:00",
            ),
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=activity_group_ids[1],
                instance_identifier="2022-07-13 07:00:00#2022-07-13 23:00:00",
            ),
        ]

        activity_group_completion_metric_dtos = [
            ActivityGroupCompletionMetricDTOFactory(
                id=activity_group_completion_metric_ids[0],
                entity_id=entity_ids[0],
                activity_group_id=activity_group_ids[0],
                value=completion_metric_target_values[0],
                entity_type=entity_types[0],
            ),
            ActivityGroupCompletionMetricDTOFactory(
                id=activity_group_completion_metric_ids[1],
                entity_id=entity_ids[1],
                activity_group_id=activity_group_ids[1],
                value=completion_metric_target_values[1],
                entity_type=entity_types[1],
            ),
        ]

        activity_group_instances_count_dtos = [
            ActivityGroupInstanceCountDTOFactory(
                activity_group_id=activity_group_ids[0],
                activity_group_instances_count=
                activity_group_instances_count[0],
            ),
            ActivityGroupInstanceCountDTOFactory(
                activity_group_id=activity_group_ids[1],
                activity_group_instances_count=
                activity_group_instances_count[1],
            ),
        ]

        user_activity_group_instance_metric_tracker_dtos = [
            UserActivityGroupInstanceMetricTrackerDTOFactory(
                user_activity_group_instance_id
                =user_activity_group_instance_ids[0],
                activity_group_completion_metric_id
                =activity_group_completion_metric_ids[0],
                current_value=
                activity_group_completion_metric_current_value[0],
            ),
            UserActivityGroupInstanceMetricTrackerDTOFactory(
                user_activity_group_instance_id
                =user_activity_group_instance_ids[1],
                activity_group_completion_metric_id
                =activity_group_completion_metric_ids[1],
                current_value=
                activity_group_completion_metric_current_value[1],
            ),
        ]

        expected_user_activity_group_instance_with_association_dtos = [
            UserActivityGroupCompletionMetricDTOFactory(
                activity_group_id=activity_group_ids[0],
                no_of_activity_group_instances_completed
                =activity_group_instances_count[0],
                instance_completion_metrics=[
                    UserCompletionMetricDTOFactory(
                        target_value=completion_metric_target_values[0],
                        current_value=
                        activity_group_completion_metric_current_value[0],
                        entity_id=entity_ids[0],
                        entity_type=entity_types[0],
                    ),
                ],
            ),
            UserActivityGroupCompletionMetricDTOFactory(
                activity_group_id=activity_group_ids[1],
                no_of_activity_group_instances_completed
                =activity_group_instances_count[1],
                instance_completion_metrics=[
                    UserCompletionMetricDTOFactory(
                        target_value=completion_metric_target_values[1],
                        current_value=
                        activity_group_completion_metric_current_value[0],
                        entity_id=entity_ids[1],
                        entity_type=entity_types[1],
                    ),
                ],
            ),
        ]

        return activity_group_completion_metric_dtos, \
            activity_group_frequency_config_dtos, activity_group_ids, \
            activity_group_instance_identifier_dtos, \
            activity_group_instances_count_dtos, \
            expected_user_activity_group_instance_with_association_dtos, \
            user_activity_group_instance_dtos, \
            user_activity_group_instance_ids,\
            user_activity_group_instance_metric_tracker_dtos, user_id

    def test_with_user_activity_group_instance_metrics(
            self, common_setup,
            empty_user_activity_group_instance_metric_trackers_setup):
        interactor, activity_group_storage_mock = common_setup
        activity_group_completion_metric_dtos, \
            activity_group_frequency_config_dtos, \
            activity_group_ids, activity_group_instance_identifier_dtos, \
            activity_group_instances_count_dtos, \
            expected_user_activity_group_instance_with_association_dtos, \
            user_activity_group_instance_dtos, \
            user_activity_group_instance_ids, \
            user_activity_group_instance_metric_tracker_dtos, user_id = \
            empty_user_activity_group_instance_metric_trackers_setup

        activity_group_storage_mock.get_activity_groups_frequency_configs\
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_user_activity_group_instances\
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_activity_groups_completion_metrics\
            .return_value = activity_group_completion_metric_dtos
        activity_group_storage_mock\
            .get_user_activity_group_instances_metric_tracker_without_transaction\
            .return_value = user_activity_group_instance_metric_tracker_dtos
        activity_group_storage_mock\
            .get_activity_group_instances_count_for_completion_status\
            .return_value = activity_group_instances_count_dtos

        actual_user_activity_group_instance_with_association_dtos = \
            interactor.get_activity_group_instance_completion_metrics(
                user_id, activity_group_ids)

        assert expected_user_activity_group_instance_with_association_dtos == \
               actual_user_activity_group_instance_with_association_dtos

        activity_group_storage_mock.get_activity_groups_frequency_configs\
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_user_activity_group_instances \
            .assert_called_once_with(user_id,
                                     activity_group_instance_identifier_dtos)
        activity_group_storage_mock.get_activity_groups_completion_metrics\
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock\
            .get_user_activity_group_instances_metric_tracker_without_transaction\
            .assert_called_once_with(user_activity_group_instance_ids)
        activity_group_storage_mock \
            .get_activity_group_instances_count_for_completion_status\
            .assert_called_once_with(user_id, activity_group_ids,
                                     CompletionStatusEnum.COMPLETED.value)

import datetime
import uuid

import factory
import freezegun
import pytest

from nw_activities.constants.enum import ActivityGroupAssociationTypeEnum, \
    FrequencyTypeEnum, FrequencyPeriodEnum, \
    WeekDayEnum, CompletionStatusEnum, CompletionMetricEntityTypeEnum
from nw_activities.tests.common_fixtures.adapters import \
    send_activity_group_completed_event_mock
from nw_activities.tests.common_fixtures.interactors import \
    get_user_activity_group_instances_with_associations_instances_mock
from nw_activities.tests.common_fixtures.utils import generate_uuid_mock
from nw_activities.tests.factories.interactor_dtos import \
    ActivityGroupInstanceDTOFactory, \
    UserActivityGroupInstanceWithAssociationDTOFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupAssociationDTOFactory, ActivityGroupFrequencyConfigDTOFactory, \
    UserActivityGroupInstanceDTOFactory, \
    ActivityGroupCompletionMetricDTOFactory, \
    UserActivityGroupInstanceMetricTrackerDTOFactory, \
    ActivityGroupInstanceIdentifierDTOFactory


@freezegun.freeze_time("2022-07-13 15:00:00")
@pytest.mark.django_db
class TestActivityGroupAssociationActivityGroupInteractor:

    @pytest.fixture
    def common_setup(self):
        from unittest.mock import create_autospec
        from nw_activities.interactors.storage_interfaces.\
            activity_group_storage_interface import \
            ActivityGroupStorageInterface
        from nw_activities.interactors.\
            update_activity_group_association_completion_metrics.activity_group\
            import ActivityGroupAssociationActivityGroupInteractor

        activity_group_storage_mock = create_autospec(
            ActivityGroupStorageInterface)
        interactor = ActivityGroupAssociationActivityGroupInteractor(
            activity_group_storage_mock)

        return interactor, activity_group_storage_mock

    @pytest.fixture
    def setup_data(self):
        user_id = str(uuid.uuid4())
        entity_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        activity_group_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        activity_group_association_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        user_activity_group_instance_ids = [str(uuid.uuid4()),
                                            str(uuid.uuid4())]
        activity_group_completion_metric_ids = [str(uuid.uuid4()),
                                                str(uuid.uuid4())]
        completion_metric_target_values = [5.0, 5.0]
        entity_types = [
            CompletionMetricEntityTypeEnum.ACTIVITY_GROUP_ASSOCIATION.value,
            CompletionMetricEntityTypeEnum.ACTIVITY_GROUP_ASSOCIATION.value,
        ]

        activity_group_association_dtos_of_type_activity = [
            ActivityGroupAssociationDTOFactory(
                activity_group_id=activity_group_ids[0],
                association_type=ActivityGroupAssociationTypeEnum
                .ACTIVITY_GROUP.value,
                association_id=entity_ids[0],
            ),
            ActivityGroupAssociationDTOFactory(
                activity_group_id=activity_group_ids[1],
                association_type=ActivityGroupAssociationTypeEnum
                .ACTIVITY_GROUP.value,
                association_id=entity_ids[1],
            ),
        ]

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
                        {
                            "value_type": FrequencyPeriodEnum.DAY.value,
                            "value": WeekDayEnum.MONDAY.value,
                        },
                    ],
                    "ends_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "23:00:00",
                        },
                        {
                            "value_type": FrequencyPeriodEnum.DAY.value,
                            "value": WeekDayEnum.SUNDAY.value,
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
                instance_identifier="2022-07-11 07:00:00#2022-07-17 23:00:00",
                completion_status=CompletionStatusEnum.YET_TO_START.value,
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

        user_activity_group_instance_metric_tracker_dtos = []

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

        activity_group_instance_with_associations = [
            UserActivityGroupInstanceWithAssociationDTOFactory(
                user_id=user_id,
                frequency_type=FrequencyTypeEnum.WEEKLY.value,
                activity_group_instance=ActivityGroupInstanceDTOFactory(
                    activity_group_id=activity_group_ids[0],
                    completion_percentage=50.0,
                    instance_identifier="2022-07-11 09:00:00#2022-07-17 21:00:00",
                    completion_status=CompletionStatusEnum.IN_PROGRESS.value,
                    start_datetime=datetime.datetime(2022, 7, 11, 9),
                    end_datetime=datetime.datetime(2022, 7, 17, 21),
                ),
                association_activity_group_instances=
                ActivityGroupInstanceDTOFactory.create_batch(
                    7, activity_group_id=activity_group_association_ids[0],
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
                    activity_group_id=activity_group_ids[1],
                    completion_percentage=60.0,
                    instance_identifier="2022-07-11 10:00:00#2022-07-17 22:00:00",
                    completion_status=CompletionStatusEnum.IN_PROGRESS.value,
                    start_datetime=datetime.datetime(2022, 7, 11, 10),
                    end_datetime=datetime.datetime(2022, 7, 17, 22),
                ),
                association_activity_group_instances=
                ActivityGroupInstanceDTOFactory.create_batch(
                    7, activity_group_id=activity_group_association_ids[1],
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
        ]

        completion_metric_entity_ids_association_dtos = [
            ActivityGroupAssociationDTOFactory(
                id=entity_ids[0],
                activity_group_id=activity_group_association_ids[0],
            ),
            ActivityGroupAssociationDTOFactory(
                id=entity_ids[1],
                activity_group_id=activity_group_association_ids[1],
            ),
        ]

        return user_id, activity_group_ids, \
            activity_group_association_dtos_of_type_activity,\
            activity_group_frequency_config_dtos,\
            user_activity_group_instance_dtos,\
            activity_group_completion_metric_dtos,\
            user_activity_group_instance_metric_tracker_dtos, \
            user_activity_group_instance_ids, \
            activity_group_completion_metric_ids, \
            activity_group_instance_identifier_dtos, \
            activity_group_instance_with_associations, \
            completion_metric_entity_ids_association_dtos

    def test_with_valid_data(self, common_setup, mocker, setup_data):
        interactor, activity_group_storage_mock = common_setup

        user_id, activity_group_ids, \
            activity_group_association_dtos_of_type_activity, \
            activity_group_frequency_config_dtos, \
            user_activity_group_instance_dtos, \
            activity_group_completion_metric_dtos, \
            user_activity_group_instance_metric_tracker_dtos, \
            user_activity_group_instance_ids, \
            activity_group_completion_metric_ids, \
            activity_group_instance_identifier_dtos, \
            activity_group_instance_with_associations, \
            completion_metric_entity_ids_association_dtos = setup_data

        user_activity_group_instance_metric_tracker_ids = [
            str(uuid.uuid4()), str(uuid.uuid4()),
        ]

        generate_uuid_mock_object = generate_uuid_mock(mocker)
        generate_uuid_mock_object.side_effect = \
            user_activity_group_instance_metric_tracker_ids

        user_activity_group_instance_metric_tracker_dtos_to_create = [
            UserActivityGroupInstanceMetricTrackerDTOFactory(
                id=user_activity_group_instance_metric_tracker_ids[0],
                user_activity_group_instance_id
                =user_activity_group_instance_ids[0],
                activity_group_completion_metric_id
                =activity_group_completion_metric_ids[0],
                current_value=2.0,
            ),
            UserActivityGroupInstanceMetricTrackerDTOFactory(
                id=user_activity_group_instance_metric_tracker_ids[1],
                user_activity_group_instance_id
                =user_activity_group_instance_ids[1],
                activity_group_completion_metric_id
                =activity_group_completion_metric_ids[1],
                current_value=1.0,
            ),
        ]

        user_activity_group_instance_dtos[0].completion_percentage = 100.0
        user_activity_group_instance_dtos[0].completion_status = \
            CompletionStatusEnum.COMPLETED.value
        user_activity_group_instance_dtos[0].completion_percentage = 50.0
        user_activity_group_instance_dtos[0].completion_status = \
            CompletionStatusEnum.IN_PROGRESS.value

        activity_group_storage_mock\
            .get_activity_group_associations_for_activity_group_ids.\
            return_value = activity_group_association_dtos_of_type_activity
        activity_group_storage_mock.get_activity_groups_frequency_configs.\
            return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_user_activity_group_instances.\
            return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_activity_groups_completion_metrics.\
            return_value = activity_group_completion_metric_dtos
        activity_group_storage_mock\
            .get_user_activity_group_instances_metric_tracker.return_value = \
            user_activity_group_instance_metric_tracker_dtos
        activity_group_storage_mock \
            .get_activity_group_associations_for_association_ids. \
            return_value = []
        activity_group_storage_mock.get_activity_group_associations\
            .return_value = completion_metric_entity_ids_association_dtos

        send_activity_group_completed_event_mock_object = \
            send_activity_group_completed_event_mock(mocker)
        get_user_agi_with_associations_instances_mock_object = \
            get_user_activity_group_instances_with_associations_instances_mock(
                mocker)
        get_user_agi_with_associations_instances_mock_object.return_value = \
            activity_group_instance_with_associations

        interactor.update_associations_completion_metrics_of_type_activity_group(
            user_id, activity_group_ids)

        activity_group_storage_mock\
            .get_activity_group_associations_for_activity_group_ids\
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock \
            .get_activity_group_associations_for_association_ids\
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_activity_groups_frequency_configs\
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_user_activity_group_instances\
            .assert_called_once_with(
                user_id, activity_group_instance_identifier_dtos)
        activity_group_storage_mock.get_activity_groups_completion_metrics\
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock\
            .get_user_activity_group_instances_metric_tracker\
            .assert_called_once_with(user_activity_group_instance_ids)
        activity_group_storage_mock\
            .create_user_activity_group_instances_metric_tracker\
            .assert_called_once_with(
                user_activity_group_instance_metric_tracker_dtos_to_create)
        activity_group_storage_mock\
            .update_user_activity_group_instances_metric_tracker\
            .assert_not_called()
        activity_group_storage_mock.update_user_activity_group_instances\
            .assert_called_once_with(user_activity_group_instance_dtos)

        send_activity_group_completed_event_mock_object.assert_not_called()

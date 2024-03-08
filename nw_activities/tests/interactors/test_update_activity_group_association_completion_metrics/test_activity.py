import uuid

import freezegun
import pytest

from nw_activities.constants.enum import TransactionTypeEnum, \
    ActivityGroupAssociationTypeEnum, FrequencyTypeEnum, FrequencyPeriodEnum, \
    WeekDayEnum, CompletionStatusEnum, CompletionMetricEntityTypeEnum
from nw_activities.tests.common_fixtures.adapters import \
    send_activity_group_completed_event_mock
from nw_activities.tests.common_fixtures.interactors import \
    update_associations_completion_metrics_of_type_activity_group, \
    create_user_activity_group_instance_rewards_mock
from nw_activities.tests.common_fixtures.utils import generate_uuid_mock
from nw_activities.tests.factories.interactor_dtos import \
    UserActivityDTOFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupAssociationDTOFactory, \
    ActivityGroupFrequencyConfigDTOFactory, \
    UserActivityGroupInstanceDTOFactory, \
    ActivityGroupCompletionMetricDTOFactory, \
    UserActivityGroupInstanceMetricTrackerDTOFactory, \
    ActivityGroupInstanceIdentifierDTOFactory


@freezegun.freeze_time("2022-07-13 15:00:00")
@pytest.mark.django_db
class TestActivityGroupAssociationActivityInteractor:

    @pytest.fixture
    def common_setup(self):
        from unittest.mock import create_autospec
        from nw_activities.interactors.storage_interfaces.\
            activity_group_storage_interface import \
            ActivityGroupStorageInterface
        from nw_activities.interactors.\
            update_activity_group_association_completion_metrics.activity \
            import ActivityGroupAssociationActivityInteractor

        activity_group_storage_mock = create_autospec(
            ActivityGroupStorageInterface)
        interactor = ActivityGroupAssociationActivityInteractor(
            activity_group_storage_mock)

        return interactor, activity_group_storage_mock

    @pytest.fixture
    def setup_data(self):
        user_id = str(uuid.uuid4())
        activity_name_enum = "ACTIVITY_NAME_ENUM"
        resource_name_enum = "RESOURCE_NAME_ENUM"
        transaction_type = TransactionTypeEnum.CREDIT.value
        resource_value = 100.0
        activity_group_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        activity_group_ids_of_type_activity_group = [str(uuid.uuid4()),
                                                     str(uuid.uuid4())]
        user_activity_group_instance_ids = [str(uuid.uuid4()),
                                            str(uuid.uuid4())]
        activity_group_completion_metric_ids = [str(uuid.uuid4()),
                                                str(uuid.uuid4())]
        completion_metric_target_values = [100.0, 200.0]
        entity_types = [CompletionMetricEntityTypeEnum.RESOURCE.value,
                        CompletionMetricEntityTypeEnum.RESOURCE.value]

        user_activity_dto = UserActivityDTOFactory(
            user_id=user_id,
            activity_name_enum=activity_name_enum,
            resource_name_enum=resource_name_enum,
            resource_value=resource_value,
            transaction_type=transaction_type,
        )

        activity_group_association_dtos_of_type_activity = [
            ActivityGroupAssociationDTOFactory(
                activity_group_id=activity_group_ids[0],
                association_type=
                ActivityGroupAssociationTypeEnum.ACTIVITY.value,
            ),
            ActivityGroupAssociationDTOFactory(
                activity_group_id=activity_group_ids[1],
                association_type=
                ActivityGroupAssociationTypeEnum.ACTIVITY.value,
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

        activity_group_completion_metric_dtos = [
            ActivityGroupCompletionMetricDTOFactory(
                id=activity_group_completion_metric_ids[0],
                entity_id=user_activity_dto.resource_name_enum,
                activity_group_id=activity_group_ids[0],
                value=completion_metric_target_values[0],
                entity_type=entity_types[0],
            ),
            ActivityGroupCompletionMetricDTOFactory(
                id=activity_group_completion_metric_ids[1],
                entity_id=user_activity_dto.resource_name_enum,
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

        activity_group_association_dtos_of_type_activity_group = [
            ActivityGroupAssociationDTOFactory(
                activity_group_id=activity_group_ids_of_type_activity_group[0],
                association_id=activity_group_ids[0],
                association_type=
                ActivityGroupAssociationTypeEnum.ACTIVITY_GROUP.value,
            ),
            ActivityGroupAssociationDTOFactory(
                activity_group_id=activity_group_ids_of_type_activity_group[1],
                association_id=activity_group_ids[1],
                association_type=
                ActivityGroupAssociationTypeEnum.ACTIVITY_GROUP.value,
            ),
        ]

        return user_activity_dto, activity_group_ids, \
            activity_group_association_dtos_of_type_activity,\
            activity_group_frequency_config_dtos,\
            user_activity_group_instance_dtos,\
            activity_group_completion_metric_dtos,\
            user_activity_group_instance_metric_tracker_dtos,\
            activity_group_association_dtos_of_type_activity_group, \
            user_activity_group_instance_ids, \
            activity_group_completion_metric_ids, \
            activity_group_instance_identifier_dtos, \
            activity_group_ids_of_type_activity_group

    def test_with_valid_data(self, common_setup, mocker, setup_data):
        interactor, activity_group_storage_mock = common_setup

        user_activity_dto, activity_group_ids, \
            activity_group_association_dtos_of_type_activity, \
            activity_group_frequency_config_dtos, \
            user_activity_group_instance_dtos, \
            activity_group_completion_metric_dtos, \
            user_activity_group_instance_metric_tracker_dtos, \
            activity_group_association_dtos_of_type_activity_group, \
            user_activity_group_instance_ids, \
            activity_group_completion_metric_ids, \
            activity_group_instance_identifier_dtos, \
            activity_group_ids_of_type_activity_group = setup_data

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
                current_value=100.0,
            ),
            UserActivityGroupInstanceMetricTrackerDTOFactory(
                id=user_activity_group_instance_metric_tracker_ids[1],
                user_activity_group_instance_id
                =user_activity_group_instance_ids[1],
                activity_group_completion_metric_id
                =activity_group_completion_metric_ids[1],
                current_value=100.0,
            ),
        ]

        user_activity_group_instance_dtos[0].completion_percentage = 100.0
        user_activity_group_instance_dtos[0].completion_status = \
            CompletionStatusEnum.COMPLETED.value
        user_activity_group_instance_dtos[0].completion_percentage = 50.0
        user_activity_group_instance_dtos[0].completion_status = \
            CompletionStatusEnum.IN_PROGRESS.value

        activity_group_storage_mock\
            .get_activity_group_associations_for_association_ids.side_effect\
            = [activity_group_association_dtos_of_type_activity,
               activity_group_association_dtos_of_type_activity_group]
        activity_group_storage_mock.get_activity_groups_frequency_configs.\
            return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_user_activity_group_instances.\
            return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_activity_groups_completion_metrics.\
            return_value = activity_group_completion_metric_dtos
        activity_group_storage_mock\
            .get_user_activity_group_instances_metric_tracker.return_value = \
            user_activity_group_instance_metric_tracker_dtos
        activity_group_storage_mock.get_streak_enabled_activity_group_ids\
            .return_value = []

        send_activity_group_completed_event_mock_object = \
            send_activity_group_completed_event_mock(mocker)
        update_associations_completion_metrics_of_type_activity_group_object \
            = update_associations_completion_metrics_of_type_activity_group(
                mocker)
        create_user_activity_group_instance_rewards_mock_object = \
            create_user_activity_group_instance_rewards_mock(mocker)

        interactor.update_associations_completion_metrics_of_type_activity(
            user_activity_dto)

        activity_group_storage_mock \
            .get_activity_group_associations_for_association_ids\
            .assert_called()
        activity_group_storage_mock.get_activity_groups_frequency_configs\
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_user_activity_group_instances\
            .assert_called_once_with(
                user_activity_dto.user_id,
                activity_group_instance_identifier_dtos)
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

        send_activity_group_completed_event_mock_object\
            .assert_called_once_with(
                user_activity_dto.user_id, activity_group_ids[0],
                activity_group_frequency_config_dtos[0].frequency_type,
            )
        update_associations_completion_metrics_of_type_activity_group_object\
            .assert_called_once_with(
                user_activity_dto.user_id,
                activity_group_ids_of_type_activity_group)
        create_user_activity_group_instance_rewards_mock_object\
            .assert_called_once_with(user_activity_dto.user_id,
                                     activity_group_ids)

import uuid

import freezegun
import pytest

from nw_activities.constants.enum import FrequencyTypeEnum,\
    FrequencyPeriodEnum, CompletionStatusEnum
from nw_activities.tests.common_fixtures.utils import generate_uuid_mock
from nw_activities.tests.factories.interactor_dtos import UserActivityDTOFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupAssociationDTOFactory, ActivityGroupFrequencyConfigDTOFactory, \
    UserActivityGroupInstanceDTOFactory, \
    ActivityGroupInstanceIdentifierDTOFactory, \
    ActivityGroupOptionalMetricDTOFactory, \
    UserActivityGroupInstanceMetricTrackerDTOFactory


@freezegun.freeze_time("2022-07-13 23:59:59")
@pytest.mark.django_db
class TestActivityGroupAssociationActivityInteractor:

    @pytest.fixture()
    def common_setup(self):
        from unittest.mock import create_autospec
        from nw_activities.interactors.storage_interfaces. \
            activity_group_storage_interface import \
            ActivityGroupStorageInterface
        from nw_activities.interactors.update_activity_group_optional_metrics. \
            activity import ActivityGroupAssociationActivityInteractor

        activity_group_storage_mock = create_autospec(
            ActivityGroupStorageInterface)
        interactor = ActivityGroupAssociationActivityInteractor(
            activity_group_storage_mock)

        return interactor, activity_group_storage_mock

    @pytest.fixture()
    def activity_setup(self, mocker):
        user_id = str(uuid.uuid4())
        user_activity_dto = UserActivityDTOFactory(user_id=user_id)

        activity_group_association_dtos = \
            ActivityGroupAssociationDTOFactory.create_batch(size=2)
        activity_group_ids = [
            dto.activity_group_id
            for dto in activity_group_association_dtos
        ]

        activity_group_frequency_config_dtos = [
            ActivityGroupFrequencyConfigDTOFactory(
                activity_group_id=activity_group_ids[0],
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
            ActivityGroupFrequencyConfigDTOFactory(
                activity_group_id=activity_group_ids[1],
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
        instance_identifiers = ["2022-07-13 08:00:00#2022-07-13 23:59:59",
                                "2022-07-13 08:00:00#2022-07-13 23:59:59"]
        uuid_ids = [
            str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()),
            str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()),
        ]
        generate_uuid_mock_object = generate_uuid_mock(mocker)
        generate_uuid_mock_object.side_effect = uuid_ids
        user_activity_group_instance_dtos = [
            UserActivityGroupInstanceDTOFactory(
                id=uuid_ids[0], user_id=user_id,
                activity_group_id=activity_group_ids[0],
                instance_identifier=instance_identifiers[0],
                completion_percentage=0,
                completion_status=CompletionStatusEnum.YET_TO_START.value,
            ),
            UserActivityGroupInstanceDTOFactory(
                id=uuid_ids[1], user_id=user_id,
                activity_group_id=activity_group_ids[1],
                instance_identifier=instance_identifiers[1],
                completion_percentage=0,
                completion_status=CompletionStatusEnum.YET_TO_START.value,
            ),
        ]
        activity_group_instance_identifier_dtos = [
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=activity_group_id,
                instance_identifier=instance_identifier,
            )
            for activity_group_id, instance_identifier in zip(
                activity_group_ids, instance_identifiers)
        ]
        user_activity_group_instance_ids = [
            dto.id for dto in user_activity_group_instance_dtos
        ]
        entity_id = "resource_name_enum_1"
        activity_group_optional_metric_dtos = [
            ActivityGroupOptionalMetricDTOFactory(
                activity_group_id=activity_group_id,
                entity_id=entity_id,
            )
            for activity_group_id in activity_group_ids
        ]

        activity_group_id_wise_optional_metric_dtos = {
            activity_group_optional_metric_dtos[0].activity_group_id: [
                activity_group_optional_metric_dtos[0],
            ],
            activity_group_optional_metric_dtos[1].activity_group_id: [
                activity_group_optional_metric_dtos[1],
            ],
        }
        user_activity_group_instance_metric_tracker_dtos = [
            UserActivityGroupInstanceMetricTrackerDTOFactory(
                id=uuid_ids[2],
                user_activity_group_instance_id
                =user_activity_group_instance_ids[0],
                activity_group_completion_metric_id=None,
                activity_group_optional_metric_id
                =activity_group_optional_metric_dtos[0].id,
                current_value=1.0,
            ),
            UserActivityGroupInstanceMetricTrackerDTOFactory(
                id=uuid_ids[3], user_activity_group_instance_id
                =user_activity_group_instance_ids[1],
                activity_group_completion_metric_id=None,
                activity_group_optional_metric_id
                =activity_group_optional_metric_dtos[1].id,
                current_value=1.0,
            ),
        ]
        return user_id, user_activity_dto, activity_group_association_dtos, \
            activity_group_ids, activity_group_frequency_config_dtos, \
            user_activity_group_instance_dtos, \
            user_activity_group_instance_ids, \
            activity_group_instance_identifier_dtos, \
            activity_group_optional_metric_dtos, \
            activity_group_id_wise_optional_metric_dtos, \
            user_activity_group_instance_metric_tracker_dtos

    def test_when_no_existing_associations_option_metrics_creates(
            self, common_setup, activity_setup):

        # Arrange
        user_id, user_activity_dto, activity_group_association_dtos, \
            activity_group_ids, activity_group_frequency_config_dtos, \
            user_activity_group_instance_dtos, \
            user_activity_group_instance_ids, \
            activity_group_instance_identifier_dtos, \
            activity_group_optional_metric_dtos, _, \
            user_activity_group_instance_metric_tracker_dtos = activity_setup

        interactor, activity_group_storage_mock = common_setup

        activity_group_storage_mock. \
            get_activity_group_associations_for_association_ids.return_value = \
            activity_group_association_dtos
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock. \
            get_user_activity_group_instances_metric_tracker.return_value = \
            []
        activity_group_storage_mock.get_user_activity_group_instances \
            .return_value = []
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .return_value = activity_group_optional_metric_dtos

        # Act
        interactor.update_associations_optional_metrics_of_type_activity(
            user_activity_dto)

        # Assert
        activity_group_storage_mock \
            .get_activity_group_associations_for_association_ids \
            .assert_called_once_with([user_activity_dto.activity_name_enum])
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_user_activity_group_instances \
            .assert_called_once_with(
                user_id, activity_group_instance_identifier_dtos)
        activity_group_storage_mock.create_user_activity_group_instances \
            .assert_called_once_with(user_activity_group_instance_dtos)
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock \
            .get_user_activity_group_instances_metric_tracker \
            .assert_called_once_with(user_activity_group_instance_ids)
        activity_group_storage_mock \
            .create_user_activity_group_instances_metric_tracker \
            .assert_called_once_with(
                user_activity_group_instance_metric_tracker_dtos)
        activity_group_storage_mock \
            .update_user_activity_group_instances_metric_tracker \
            .assert_not_called()

    def test_when_existing_associations_option_metrics_updates(
            self, common_setup, activity_setup):

        # Arrange
        user_id, user_activity_dto, activity_group_association_dtos, \
            activity_group_ids, activity_group_frequency_config_dtos, \
            user_activity_group_instance_dtos, \
            user_activity_group_instance_ids, \
            activity_group_instance_identifier_dtos, \
            activity_group_optional_metric_dtos, _, \
            user_activity_group_instance_metric_tracker_dtos = activity_setup

        interactor, activity_group_storage_mock = common_setup

        activity_group_storage_mock. \
            get_activity_group_associations_for_association_ids.return_value = \
            activity_group_association_dtos
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock. \
            get_user_activity_group_instances_metric_tracker.return_value = \
            user_activity_group_instance_metric_tracker_dtos
        activity_group_storage_mock.get_user_activity_group_instances \
            .return_value = []
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .return_value = activity_group_optional_metric_dtos

        # Act
        interactor.update_associations_optional_metrics_of_type_activity(
            user_activity_dto)

        # Assert
        activity_group_storage_mock \
            .get_activity_group_associations_for_association_ids \
            .assert_called_once_with([user_activity_dto.activity_name_enum])
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_user_activity_group_instances \
            .assert_called_once_with(user_id,
                                     activity_group_instance_identifier_dtos)
        activity_group_storage_mock.create_user_activity_group_instances \
            .assert_called_once_with(user_activity_group_instance_dtos)
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock \
            .get_user_activity_group_instances_metric_tracker \
            .assert_called_once_with(user_activity_group_instance_ids)
        activity_group_storage_mock \
            .create_user_activity_group_instances_metric_tracker \
            .assert_not_called()
        activity_group_storage_mock \
            .update_user_activity_group_instances_metric_tracker \
            .assert_called_once_with(
                user_activity_group_instance_metric_tracker_dtos)

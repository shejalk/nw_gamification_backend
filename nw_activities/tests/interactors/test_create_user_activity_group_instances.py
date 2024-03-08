import datetime
import uuid

import freezegun
import pytest

from nw_activities.constants.enum import FrequencyTypeEnum, \
    FrequencyPeriodEnum, InstanceTypeEnum, CompletionStatusEnum
from nw_activities.exceptions.custom_exceptions import \
    InvalidInstanceTypesException
from nw_activities.tests.common_fixtures.adapters import \
    is_activity_groups_enabled_for_users_mock
from nw_activities.tests.common_fixtures.utils import generate_uuid_mock
from nw_activities.tests.factories.adapter_dtos import \
    UserActivityGroupEnabledDTOFactory
from nw_activities.tests.factories.interactor_dtos import \
    UserInstanceTypeDTOFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupFrequencyConfigDTOFactory, \
    ActivityGroupInstanceIdentifierDTOFactory, \
    UserActivityGroupInstanceDTOFactory


@freezegun.freeze_time("2022-07-13 23:59:59")
class TestCreateUserActivityGroupInstanceInteractor:

    @pytest.fixture()
    def common_setup(self):
        from unittest.mock import create_autospec
        from nw_activities.interactors.storage_interfaces. \
            activity_group_storage_interface import \
            ActivityGroupStorageInterface
        from nw_activities.interactors.create_user_activity_group_instances \
            import CreateUserActivityGroupInstanceInteractor

        activity_group_storage_mock = create_autospec(
            ActivityGroupStorageInterface)
        interactor = CreateUserActivityGroupInstanceInteractor(
            activity_group_storage_mock)

        return interactor, activity_group_storage_mock

    @pytest.fixture()
    def activity_setup(self, mocker):
        user_id = str(uuid.uuid4())
        activity_group_ids = [str(uuid.uuid4())]

        user_instance_type_dtos = [
            UserInstanceTypeDTOFactory(user_id=user_id),
        ]
        user_activity_group_enabled_dto = UserActivityGroupEnabledDTOFactory(
            user_id=user_id, activity_group_enabled=True)

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
        ]

        instance_identifiers = ["2022-07-13 08:00:00#2022-07-13 23:59:59",
                                "2022-07-13 08:00:00#2022-07-13 23:59:59"]
        uuid_ids = [
            str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()),
            str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()),
        ]
        generate_uuid_mock_object = generate_uuid_mock(mocker)
        generate_uuid_mock_object.side_effect = uuid_ids

        activity_group_instance_identifier_dtos = [
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=activity_group_ids[0],
                instance_identifier=instance_identifiers[0],
            ),
        ]
        user_activity_group_instance_dtos = [
            UserActivityGroupInstanceDTOFactory(
                id=uuid_ids[0], user_id=user_id,
                activity_group_id=activity_group_ids[0],
                instance_identifier=instance_identifiers[0],
                completion_percentage=0,
                completion_status=CompletionStatusEnum.YET_TO_START.value,
            ),
        ]

        return user_id, activity_group_ids, user_instance_type_dtos, \
            user_activity_group_enabled_dto, \
            activity_group_frequency_config_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_instance_dtos

    def test_create_user_agi_with_invalid_instance_type_raises_exception(
            self, common_setup, activity_setup):
        # Arrange
        interactor, _ = common_setup
        _, _, user_instance_type_dtos, _, _, _, _ = activity_setup

        instance_type = "INVALID_INSTANCE"
        user_instance_type_dtos[0].instance_type = instance_type

        # Assert
        with pytest.raises(InvalidInstanceTypesException):
            interactor\
                .create_user_activity_group_instance_with_daily_frequency(
                    user_instance_type_dtos)

    def test_create_user_agsi_with_invalid_instance_type_raises_exception(
            self, common_setup, activity_setup):
        # Arrange
        interactor, _ = common_setup
        _, _, user_instance_type_dtos, _, _, _, _ = activity_setup
        instance_type = "INVALID_INSTANCE"
        user_instance_type_dtos[0].instance_type = instance_type

        # Assert
        with pytest.raises(InvalidInstanceTypesException):
            interactor. \
                create_user_activity_group_streak_instance_with_daily_frequency \
                (user_instance_type_dtos)

    def test_when_no_existing_activity_group_instances_creates(
            self, common_setup, activity_setup, mocker):
        interactor, activity_group_storage_mock = common_setup
        user_id, activity_group_ids, user_instance_type_dtos, \
            user_activity_group_enabled_dto, \
            activity_group_frequency_config_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_instance_dtos = activity_setup

        is_activity_groups_enabled_for_users_mock_object = \
            is_activity_groups_enabled_for_users_mock(
                mocker, [user_id])
        is_activity_groups_enabled_for_users_mock_object.return_value = \
            [user_activity_group_enabled_dto]
        activity_group_storage_mock.get_all_activity_group_ids.return_value = \
            activity_group_ids
        activity_group_storage_mock.get_streak_enabled_activity_group_ids \
            .return_value = []
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_users_activity_group_instances \
            .return_value = []

        # Act
        interactor.create_user_activity_group_instance_with_daily_frequency(
            user_instance_type_dtos)

        # Assert
        activity_group_storage_mock.get_all_activity_group_ids \
            .assert_called_once()
        activity_group_storage_mock.get_streak_enabled_activity_group_ids \
            .assert_called_once()
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_users_activity_group_instances \
            .assert_called_once_with(
                [user_id], activity_group_instance_identifier_dtos)
        activity_group_storage_mock.create_user_activity_group_instances \
            .assert_called_once_with(user_activity_group_instance_dtos)
        activity_group_storage_mock.update_user_activity_group_instances \
            .assert_not_called()

    def test_when_existing_activity_group_instances_updates(
            self, common_setup, activity_setup, mocker):
        interactor, activity_group_storage_mock = common_setup
        user_id, activity_group_ids, user_instance_type_dtos, \
            user_activity_group_enabled_dto, \
            activity_group_frequency_config_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_instance_dtos = activity_setup

        is_activity_groups_enabled_for_users_mock_object = \
            is_activity_groups_enabled_for_users_mock(
                mocker, [user_id])
        is_activity_groups_enabled_for_users_mock_object.return_value = \
            [user_activity_group_enabled_dto]
        activity_group_storage_mock.get_all_activity_group_ids.return_value = \
            activity_group_ids
        activity_group_storage_mock.get_streak_enabled_activity_group_ids \
            .return_value = []
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_users_activity_group_instances \
            .return_value = user_activity_group_instance_dtos

        # Act
        interactor.create_user_activity_group_instance_with_daily_frequency(
            user_instance_type_dtos)

        # Assert
        activity_group_storage_mock.get_all_activity_group_ids \
            .assert_called_once()
        activity_group_storage_mock.get_streak_enabled_activity_group_ids \
            .assert_called_once()
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_users_activity_group_instances \
            .assert_called_once_with(
                [user_id], activity_group_instance_identifier_dtos)
        activity_group_storage_mock.create_user_activity_group_instances. \
            assert_not_called()

        activity_group_storage_mock.update_user_activity_group_instances \
            .assert_called_once_with(user_activity_group_instance_dtos)

    def test_when_no_existing_activity_group_streak_instances_creates(
            self, common_setup, activity_setup):
        # Arrange
        interactor, activity_group_storage_mock = common_setup
        user_id, activity_group_ids, user_instance_type_dtos, _, \
            activity_group_frequency_config_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_instance_dtos = activity_setup

        activity_group_storage_mock.get_streak_enabled_activity_group_ids \
            .return_value = activity_group_ids
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_users_activity_group_instances \
            .return_value = []

        # Act
        interactor. \
            create_user_activity_group_streak_instance_with_daily_frequency(
                user_instance_type_dtos)

        # Assert
        activity_group_storage_mock.get_streak_enabled_activity_group_ids\
            .assert_called_once()
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_users_activity_group_instances\
            .assert_called_once_with(
                [user_id], activity_group_instance_identifier_dtos)
        activity_group_storage_mock.create_user_activity_group_instances\
            .assert_called_once_with(user_activity_group_instance_dtos)
        activity_group_storage_mock.update_user_activity_group_instances\
            .assert_not_called()
        activity_group_storage_mock.delete_user_activity_group_instances\
            .assert_not_called()

    def test_when_existing_activity_group_streak_instances_updates(
            self, common_setup, activity_setup):
        # Arrange
        interactor, activity_group_storage_mock = common_setup
        user_id, activity_group_ids, user_instance_type_dtos, _, \
            activity_group_frequency_config_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_instance_dtos = activity_setup

        activity_group_storage_mock.get_streak_enabled_activity_group_ids \
            .return_value = activity_group_ids
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_users_activity_group_instances \
            .return_value = user_activity_group_instance_dtos

        # Act
        interactor. \
            create_user_activity_group_streak_instance_with_daily_frequency(
                user_instance_type_dtos)

        # Assert
        activity_group_storage_mock.get_streak_enabled_activity_group_ids\
            .assert_called_once()
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_users_activity_group_instances\
            .assert_called_once_with(
                [user_id], activity_group_instance_identifier_dtos)
        activity_group_storage_mock.create_user_activity_group_instances \
            .assert_not_called()
        activity_group_storage_mock.update_user_activity_group_instances \
            .assert_called_once_with(user_activity_group_instance_dtos)
        activity_group_storage_mock.delete_user_activity_group_instances \
            .assert_not_called()

    def test_when_activity_group_streak_instance_type_paused_deletes(
            self, common_setup, activity_setup):
        # Arrange
        interactor, activity_group_storage_mock = common_setup
        user_id, activity_group_ids, user_instance_type_dtos, _, \
            activity_group_frequency_config_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_instance_dtos = activity_setup
        user_instance_type_dtos[0].instance_type = \
            InstanceTypeEnum.PAUSED.value
        user_activity_group_instance_dtos[0].instance_type = \
            InstanceTypeEnum.PAUSED.value

        activity_group_storage_mock.get_streak_enabled_activity_group_ids \
            .return_value = activity_group_ids
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_users_activity_group_instances \
            .return_value = user_activity_group_instance_dtos

        # Act
        interactor. \
            create_user_activity_group_streak_instance_with_daily_frequency(
                user_instance_type_dtos)

        # Assert
        activity_group_storage_mock.get_streak_enabled_activity_group_ids\
            .assert_called_once()
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_users_activity_group_instances\
            .assert_called_once_with(
                [user_id], activity_group_instance_identifier_dtos)
        activity_group_storage_mock.create_user_activity_group_instances \
            .assert_not_called()
        activity_group_storage_mock.update_user_activity_group_instances \
            .assert_not_called()
        activity_group_storage_mock.delete_user_activity_group_instances \
            .assert_called_once_with([user_activity_group_instance_dtos[0].id])

    def test_delete_streak_users_activity_group_instances_with_daily_frequency(
            self, common_setup, activity_setup):
        # Arrange
        interactor, activity_group_storage_mock = common_setup
        user_id, activity_group_ids, _, _, \
            activity_group_frequency_config_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_instance_dtos = activity_setup
        instance_date = datetime.date(2022, 7, 13)

        activity_group_storage_mock.get_streak_enabled_activity_group_ids \
            .return_value = activity_group_ids
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_users_activity_group_instances \
            .return_value = user_activity_group_instance_dtos

        user_activity_group_instance_ids = [
            dto.id
            for dto in user_activity_group_instance_dtos
        ]

        # Act
        interactor. \
            delete_streak_users_activity_group_instances_with_daily_frequency(
                [user_id], instance_date)

        # Assert
        activity_group_storage_mock.get_streak_enabled_activity_group_ids \
            .assert_called_once()
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_users_activity_group_instances \
            .assert_called_once_with(
                [user_id], activity_group_instance_identifier_dtos)
        activity_group_storage_mock.delete_user_activity_group_instances\
            .assert_called_once_with(user_activity_group_instance_ids)

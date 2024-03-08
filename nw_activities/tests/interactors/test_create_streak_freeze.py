import datetime
from unittest.mock import create_autospec

import pytest
from freezegun import freeze_time
from nw_activities.constants.enum import ResourceNameEnum, InstanceTypeEnum, \
    TransactionTypeEnum, StreakFreezeActivityNameEnum
from nw_activities.interactors.create_streak_freeze import \
    CreateStreakFreezeInteractor
from nw_activities.presenters.streak_freeze_presenter_implementation import \
    StreakFreezePresenterImplementation
from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.common_fixtures.adapters import \
    get_user_resource_mock, update_user_resources_mock
from nw_activities.tests.common_fixtures.interactors import \
    get_user_streak_activity_group_instances_in_given_dates_mock, \
    get_user_streak_activity_group_instances_between_given_dates_mock, \
    create_user_activity_group_streak_instance_with_daily_frequency_mock
from nw_activities.tests.factories.adapter_dtos import \
    UpdateUserResourceDTOFactory, UserResourceDTOFactory
from nw_activities.tests.factories.interactor_dtos import \
    UserInstanceTypeDTOFactory
from nw_activities.tests.factories.storage_dtos import \
    UserActivityGroupInstanceWithDatetimeDTOFactory


@pytest.mark.django_db
class TestCreateStreakFreezeInteractor:
    @pytest.fixture
    def common_setup_data(self, mocker):
        user_id = "8bbc0356-63fb-4eed-9dc2-dc407f751f38"
        storage = create_autospec(ActivityGroupStorageImplementation)
        interactor = CreateStreakFreezeInteractor(storage)
        presenter = create_autospec(StreakFreezePresenterImplementation)
        get_user_streak_agis_between_given_dates_mock_object = \
            get_user_streak_activity_group_instances_between_given_dates_mock(
                mocker)
        get_user_streak_agis_in_given_dates_mock_object = \
            get_user_streak_activity_group_instances_in_given_dates_mock(
                mocker)
        update_user_resources_mock_object = update_user_resources_mock(mocker)
        get_user_resource_mock_object = get_user_resource_mock(mocker)

        return user_id, storage, interactor, presenter, \
            get_user_streak_agis_between_given_dates_mock_object, \
            get_user_streak_agis_in_given_dates_mock_object, \
            update_user_resources_mock_object, get_user_resource_mock_object

    @freeze_time("2023-05-17 20:22:46")
    def test_create_streak_freeze_when_no_freeze_balance(
            self, common_setup_data):
        # Arrange
        user_id, _, interactor, presenter, \
            get_user_streak_agis_between_given_dates_mock_object, \
            get_user_streak_agis_in_given_dates_mock_object, \
            update_user_resources_mock_object, get_user_resource_mock_object = \
            common_setup_data
        get_user_resource_mock_object.return_value = \
            UserResourceDTOFactory(
                resource_name_enum=ResourceNameEnum.STREAK_FREEZES.value,
                final_value=0)
        instance_date = datetime.date(2023, 5, 18)
        get_user_streak_agis_in_given_dates_mock_object.return_value = []

        # Act
        _ = interactor.create_streak_freeze_wrapper(
            user_id=user_id, instance_date=instance_date, presenter=presenter,
        )

        # Assert

        get_user_resource_mock_object.assert_called_once_with(
            user_id, ResourceNameEnum.STREAK_FREEZES.value)
        assert update_user_resources_mock_object.call_count == 0
        assert get_user_streak_agis_between_given_dates_mock_object. \
                   call_count == 0
        assert get_user_streak_agis_in_given_dates_mock_object. \
                   call_count == 1
        presenter.raise_insufficient_streak_freeze_left_exception. \
            assert_called_once_with(0)

    @freeze_time("2023-05-17 20:22:46")
    def test_create_streak_freeze_when_given_date_already_frozen(
            self, common_setup_data):
        # Arrange
        user_id, _, interactor, presenter, \
            get_user_streak_agis_between_given_dates_mock_object, \
            get_user_streak_agis_in_given_dates_mock_object, \
            update_user_resources_mock_object, get_user_resource_mock_object = \
            common_setup_data
        get_user_resource_mock_object.return_value = \
            UserResourceDTOFactory(
                resource_name_enum=ResourceNameEnum.STREAK_FREEZES.value,
                final_value=0)
        instance_date = datetime.date(2023, 5, 18)
        get_user_streak_agis_in_given_dates_mock_object.return_value = [
            UserActivityGroupInstanceWithDatetimeDTOFactory(
                instance_type=InstanceTypeEnum.FREEZE.value),
        ]

        # Act
        _ = interactor.create_streak_freeze_wrapper(
            user_id=user_id, instance_date=instance_date, presenter=presenter,
        )

        # Assert

        get_user_resource_mock_object.assert_not_called()
        assert update_user_resources_mock_object.call_count == 0
        get_user_streak_agis_between_given_dates_mock_object. \
            assert_not_called()
        get_user_streak_agis_in_given_dates_mock_object.assert_called_with(
            user_id, [instance_date], [InstanceTypeEnum.FREEZE.value])
        presenter.raise_streak_freeze_already_exists_exception. \
            assert_called_once_with(instance_date)

    @freeze_time("2023-05-17 20:22:46")
    def test_for_monthly_freeze_limit_exceeded_exception(
            self, common_setup_data):
        # Arrange
        user_id, _, interactor, presenter, \
            get_user_streak_agis_between_given_dates_mock_object, \
            get_user_streak_agis_in_given_dates_mock_object, \
            update_user_resources_mock_object, get_user_resource_mock_object = \
            common_setup_data
        get_user_resource_mock_object.return_value = \
            UserResourceDTOFactory(
                resource_name_enum=ResourceNameEnum.STREAK_FREEZES.value,
                final_value=1)
        instance_date = datetime.date(2023, 5, 18)
        month_start_date = datetime.date(2023, 5, 1)
        month_end_date = datetime.date(2023, 5, 31)
        get_user_streak_agis_in_given_dates_mock_object.return_value = []
        get_user_streak_agis_between_given_dates_mock_object.return_value = [
            UserActivityGroupInstanceWithDatetimeDTOFactory(
                instance_type=InstanceTypeEnum.FREEZE.value)
            for each in range(5)
        ]

        # Act
        _ = interactor.create_streak_freeze_wrapper(
            user_id=user_id, instance_date=instance_date, presenter=presenter,
        )

        # Assert

        get_user_resource_mock_object.assert_called_once_with(
            user_id, ResourceNameEnum.STREAK_FREEZES.value)
        update_user_resources_mock_object.assert_not_called()
        get_user_streak_agis_between_given_dates_mock_object. \
            assert_called_with(user_id, month_start_date, month_end_date,
                               [InstanceTypeEnum.FREEZE.value])
        get_user_streak_agis_in_given_dates_mock_object.assert_called_once_with(
            user_id, [instance_date], [InstanceTypeEnum.FREEZE.value])
        presenter.raise_monthly_freeze_limit_exceeded_exception. \
            assert_called_once_with(5, 3)

    @freeze_time("2023-05-17 20:22:46")
    def test_create_streak_freeze(self, common_setup_data, mocker):
        # Arrange
        user_id, _, interactor, presenter, \
            get_user_streak_agis_between_given_dates_mock_object, \
            get_user_streak_agis_in_given_dates_mock_object, \
            update_user_resources_mock_object, get_user_resource_mock_object = \
            common_setup_data
        create_user_agsi_with_daily_frequency_mock_object = \
            create_user_activity_group_streak_instance_with_daily_frequency_mock(
                mocker)
        get_user_resource_mock_object.return_value = \
            UserResourceDTOFactory(
                resource_name_enum=ResourceNameEnum.STREAK_FREEZES.value,
                final_value=1)
        user_instance_type_dtos = [
            UserInstanceTypeDTOFactory.create(
                user_id=user_id,
                instance_type=InstanceTypeEnum.FREEZE.value),
        ]
        instance_date = datetime.date(2023, 5, 18)
        month_start_date = datetime.date(2023, 5, 1)
        month_end_date = datetime.date(2023, 5, 31)
        get_user_streak_agis_in_given_dates_mock_object.return_value = []
        get_user_streak_agis_between_given_dates_mock_object.return_value = []
        update_user_resource_dtos = [
            UpdateUserResourceDTOFactory(
                user_id=user_id,
                name_enum=ResourceNameEnum.STREAK_FREEZES.value,
                value=1,
                transaction_type=TransactionTypeEnum.DEBIT.value,
                activity_id=StreakFreezeActivityNameEnum.STREAK_FREEZE.value,
                entity_id=None,
                entity_type=None,
            ),
        ]

        # Act
        _ = interactor.create_streak_freeze_wrapper(
            user_id=user_id, instance_date=instance_date, presenter=presenter,
        )

        # Assert

        get_user_resource_mock_object.assert_called_once_with(
            user_id, ResourceNameEnum.STREAK_FREEZES.value)
        update_user_resources_mock_object.assert_called_once_with(
            update_user_resource_dtos)
        get_user_streak_agis_between_given_dates_mock_object. \
            assert_called_with(user_id, month_start_date, month_end_date,
                               [InstanceTypeEnum.FREEZE.value])
        get_user_streak_agis_in_given_dates_mock_object.assert_called_once_with(
            user_id, [instance_date], [InstanceTypeEnum.FREEZE.value])
        presenter.get_streak_freeze_created_success_response.assert_called_once()
        create_user_agsi_with_daily_frequency_mock_object. \
            assert_called_once_with(user_instance_type_dtos, instance_date)

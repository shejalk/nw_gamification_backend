import datetime
from unittest.mock import create_autospec

import pytest
from freezegun import freeze_time
from nw_activities.constants.enum import ResourceNameEnum, InstanceTypeEnum, \
    TransactionTypeEnum, StreakFreezeActivityNameEnum
from nw_activities.interactors.cancel_user_streak_freeze import \
    CancelUserStreakFreezeInteractor
from nw_activities.presenters.streak_freeze_presenter_implementation import \
    StreakFreezePresenterImplementation
from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.common_fixtures.adapters import \
    update_user_resources_mock
from nw_activities.tests.common_fixtures.interactors import \
    get_user_streak_activity_group_instances_in_given_dates_mock, \
    delete_user_activity_group_streak_instance_with_daily_frequency_mock
from nw_activities.tests.factories.adapter_dtos import \
    UpdateUserResourceDTOFactory
from nw_activities.tests.factories.storage_dtos import \
    UserActivityGroupInstanceWithDatetimeDTOFactory


@pytest.mark.django_db
class TestCancelStreakFreezeInteractor:
    @pytest.fixture
    def common_setup_data(self, mocker):
        user_id = "8bbc0356-63fb-4eed-9dc2-dc407f751f38"
        storage = create_autospec(ActivityGroupStorageImplementation)
        interactor = CancelUserStreakFreezeInteractor(storage)
        presenter = create_autospec(StreakFreezePresenterImplementation)
        get_user_streak_agis_in_given_dates_mock_object = \
            get_user_streak_activity_group_instances_in_given_dates_mock(
                mocker)
        update_user_resources_mock_object = update_user_resources_mock(mocker)
        delete_user_agsi_instance_mock = \
            delete_user_activity_group_streak_instance_with_daily_frequency_mock(
                mocker)

        return user_id, storage, interactor, presenter, \
            get_user_streak_agis_in_given_dates_mock_object, \
            update_user_resources_mock_object, delete_user_agsi_instance_mock

    @freeze_time("2023-05-17")
    def test_for_streak_freeze_not_found(self, common_setup_data):
        # Arrange
        user_id, _, interactor, presenter, \
            get_user_streak_agis_in_given_dates_mock_object, \
            update_user_resources_mock_object, \
            delete_user_agsi_instance_mock = common_setup_data
        instance_date = datetime.date(2023, 5, 17)
        get_user_streak_agis_in_given_dates_mock_object.return_value = []

        # Act
        response = interactor.cancel_user_streak_freeze_wrapper(user_id,
                                                                instance_date,
                                                                presenter)

        # Assert
        assert response == presenter.raise_streak_freeze_not_found_exception(
            instance_date)
        get_user_streak_agis_in_given_dates_mock_object.assert_called_once_with(
            user_id, [instance_date], [InstanceTypeEnum.FREEZE.value])
        update_user_resources_mock_object.assert_not_called()
        delete_user_agsi_instance_mock.assert_not_called()

    def test_delete_streak_freeze(self, common_setup_data):
        # Arrange
        user_id, _, interactor, presenter, \
            get_user_streak_agis_in_given_dates_mock_object, \
            update_user_resources_mock_object, delete_user_agsi_instance_mock \
            = common_setup_data
        instance_date = datetime.date(2023, 5, 17)
        get_user_streak_agis_in_given_dates_mock_object.return_value = [
            UserActivityGroupInstanceWithDatetimeDTOFactory(
                user_id=user_id,
                instance_type=InstanceTypeEnum.FREEZE.value,
            ),
        ]
        update_user_resource_dto = [
            UpdateUserResourceDTOFactory(
                user_id=user_id,
                name_enum=ResourceNameEnum.STREAK_FREEZES.value,
                value=1,
                transaction_type=TransactionTypeEnum.CREDIT.value,
                activity_id=StreakFreezeActivityNameEnum.STREAK_UNFREEZE.value,
                entity_id=None,
                entity_type=None,
            ),
        ]

        # Act
        _ = interactor.cancel_user_streak_freeze_wrapper(
            user_id, instance_date, presenter)

        # Assert

        get_user_streak_agis_in_given_dates_mock_object.assert_called_once_with(
            user_id, [instance_date], [InstanceTypeEnum.FREEZE.value])
        update_user_resources_mock_object.assert_called_once_with(
            update_user_resource_dto)
        delete_user_agsi_instance_mock.assert_called_once_with(
            [user_id], instance_date)

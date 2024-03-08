import datetime
import uuid

import pytest

from nw_activities.tests.factories.interactor_dtos import \
    UserActivityDTOFactory


class TestCreateUserActivityInteractor:

    @pytest.fixture
    def common_setup(self):
        from unittest.mock import create_autospec
        from nw_activities.interactors.storage_interfaces.\
            activity_storage_interface import ActivityStorageInterface
        from nw_activities.interactors.interface_interactors.\
            get_user_activities import \
            GetUserActivityInteractor
        from nw_activities.interactors.storage_interfaces.\
            activity_group_storage_interface import \
            ActivityGroupStorageInterface

        activity_storage_mock = create_autospec(ActivityStorageInterface)
        activity_group_storage_mock = create_autospec(
            ActivityGroupStorageInterface)
        interactor = GetUserActivityInteractor(
            activity_storage_mock, activity_group_storage_mock)

        return activity_storage_mock, activity_group_storage_mock, interactor

    def test_get_user_activities(self, common_setup):
        # Arrange
        activity_storage_mock, _, interactor = common_setup
        user_id = str(uuid.uuid4())
        from_datetime = datetime.datetime(2022, 10, 31)
        to_datetime = datetime.datetime(2022, 11, 1)

        user_activities = UserActivityDTOFactory.create_batch(2)

        activity_storage_mock.get_user_activities.return_value = \
            user_activities

        # Act
        response = interactor.get_user_activities(
            user_id, from_datetime, to_datetime)

        # Assert
        assert response == user_activities
        activity_storage_mock.get_user_activities.assert_called_once_with(
            user_id, from_datetime, to_datetime)

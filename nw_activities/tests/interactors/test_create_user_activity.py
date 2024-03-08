import uuid

import pytest

from nw_activities.exceptions.custom_exceptions import InvalidActivityException
from nw_activities.tests.common_fixtures.adapters import \
    is_user_has_access_to_perform_activities_mock, update_user_resources_mock, \
    update_user_club_leaderboards_mock, \
    is_activity_groups_enabled_for_users_mock, is_streak_enabled_mock
from nw_activities.tests.common_fixtures.interactors import \
    update_associations_completion_metrics_of_type_activity_mock
from nw_activities.tests.factories.adapter_dtos import \
    UpdateUserResourceDTOFactory, UserActivityGroupEnabledDTOFactory
from nw_activities.tests.factories.interactor_dtos import UserActivityDTOFactory


class TestCreateUserActivityInteractor:

    @pytest.fixture
    def common_setup(self):
        from unittest.mock import create_autospec
        from nw_activities.interactors.storage_interfaces.\
            activity_storage_interface import ActivityStorageInterface
        from nw_activities.interactors.storage_interfaces. \
            activity_group_storage_interface import \
            ActivityGroupStorageInterface
        from nw_activities.interactors.create_user_activity import \
            CreateUserActivityInteractor

        activity_storage_mock = create_autospec(ActivityStorageInterface)
        activity_group_storage_mock = create_autospec(
            ActivityGroupStorageInterface)
        interactor = CreateUserActivityInteractor(
            activity_storage_mock, activity_group_storage_mock)

        return activity_storage_mock, activity_group_storage_mock, interactor

    def test_when_user_has_no_access_to_perform_activities(
            self, common_setup, mocker):
        activity_storage_mock, _, interactor = common_setup
        user_id = str(uuid.uuid4())

        user_activity_dto = UserActivityDTOFactory(user_id=user_id)

        is_user_has_access_to_perform_activities_mock_object = \
            is_user_has_access_to_perform_activities_mock(mocker, False)

        interactor.create_user_activity(user_activity_dto)

        is_user_has_access_to_perform_activities_mock_object\
            .assert_called_once_with(user_id)
        activity_storage_mock.is_valid_activity.assert_not_called()

    def test_when_with_invalid_activity_name_enum_raises_exception(
            self, common_setup, mocker):
        activity_storage_mock, _, interactor = common_setup
        user_id = str(uuid.uuid4())

        user_activity_dto = UserActivityDTOFactory(user_id=user_id)

        is_user_has_access_to_perform_activities_mock_object = \
            is_user_has_access_to_perform_activities_mock(mocker, True)
        is_streak_enabled_mock_object = is_streak_enabled_mock(mocker, False)
        activity_storage_mock.is_valid_activity.return_value = False

        with pytest.raises(InvalidActivityException):
            interactor.create_user_activity(user_activity_dto)

        is_user_has_access_to_perform_activities_mock_object\
            .assert_called_once_with(user_id)
        is_streak_enabled_mock_object.assert_called_once_with(user_id)
        activity_storage_mock.is_valid_activity.assert_called_once_with(
            user_activity_dto.activity_name_enum)

    def test_when_activity_groups_are_not_enabled_to_user(
            self, common_setup, mocker):
        activity_storage_mock, _, interactor = common_setup
        user_id = str(uuid.uuid4())

        user_activity_dto = UserActivityDTOFactory(user_id=user_id)
        update_resource_dto = UpdateUserResourceDTOFactory(
            user_id=user_id,
            name_enum=user_activity_dto.resource_name_enum,
            value=user_activity_dto.resource_value,
            transaction_type=user_activity_dto.transaction_type,
            activity_id=user_activity_dto.activity_name_enum,
            entity_id=user_activity_dto.entity_id,
            entity_type=user_activity_dto.entity_type,
        )
        user_activity_group_enabled_dto = UserActivityGroupEnabledDTOFactory(
            user_id=user_id)

        is_user_has_access_to_perform_activities_mock_object = \
            is_user_has_access_to_perform_activities_mock(mocker, True)
        is_streak_enabled_mock_object = is_streak_enabled_mock(mocker, False)
        activity_storage_mock.is_valid_activity.return_value = True
        update_user_resources_mock_object = update_user_resources_mock(mocker)
        update_user_club_leaderboards_mock_object = \
            update_user_club_leaderboards_mock(mocker)
        is_activity_groups_enabled_for_users_mock_object = \
            is_activity_groups_enabled_for_users_mock(
                mocker, [user_activity_group_enabled_dto])
        update_associations_completion_metrics_of_type_activity_mock_object = \
            update_associations_completion_metrics_of_type_activity_mock(mocker)

        interactor.create_user_activity(user_activity_dto)

        is_user_has_access_to_perform_activities_mock_object\
            .assert_called_once_with(user_id)
        is_streak_enabled_mock_object.assert_called_once_with(user_id)
        activity_storage_mock.is_valid_activity.assert_called_once_with(
            user_activity_dto.activity_name_enum)
        activity_storage_mock.create_user_activity_log\
            .assert_called_once_with(user_activity_dto)
        update_user_resources_mock_object.assert_called_once_with(
            [update_resource_dto])
        update_user_club_leaderboards_mock_object.assert_called_once_with(
            user_id, user_activity_dto.resource_value,
            user_activity_dto.resource_name_enum)
        is_activity_groups_enabled_for_users_mock_object\
            .assert_called_once_with([user_id])
        update_associations_completion_metrics_of_type_activity_mock_object\
            .assert_not_called()

    def test_when_activity_groups_are_enabled_to_user(
            self, common_setup, mocker):
        activity_storage_mock, _, interactor = common_setup
        user_id = str(uuid.uuid4())

        user_activity_dto = UserActivityDTOFactory(user_id=user_id)
        update_resource_dto = UpdateUserResourceDTOFactory(
            user_id=user_id,
            name_enum=user_activity_dto.resource_name_enum,
            value=user_activity_dto.resource_value,
            transaction_type=user_activity_dto.transaction_type,
            activity_id=user_activity_dto.activity_name_enum,
            entity_id=user_activity_dto.entity_id,
            entity_type=user_activity_dto.entity_type,
        )
        user_activity_group_enabled_dto = UserActivityGroupEnabledDTOFactory(
            user_id=user_id, activity_group_enabled=True)

        is_user_has_access_to_perform_activities_mock_object = \
            is_user_has_access_to_perform_activities_mock(mocker, True)
        is_streak_enabled_mock_object = is_streak_enabled_mock(mocker, False)
        activity_storage_mock.is_valid_activity.return_value = True
        update_user_resources_mock_object = update_user_resources_mock(mocker)
        update_user_club_leaderboards_mock_object = \
            update_user_club_leaderboards_mock(mocker)
        is_activity_groups_enabled_for_users_mock_object = \
            is_activity_groups_enabled_for_users_mock(
                mocker, [user_activity_group_enabled_dto])
        update_associations_completion_metrics_of_type_activity_mock_object = \
            update_associations_completion_metrics_of_type_activity_mock(mocker)

        interactor.create_user_activity(user_activity_dto)

        is_user_has_access_to_perform_activities_mock_object\
            .assert_called_once_with(user_id)
        is_streak_enabled_mock_object.assert_called_once_with(user_id)
        activity_storage_mock.is_valid_activity.assert_called_once_with(
            user_activity_dto.activity_name_enum)
        activity_storage_mock.create_user_activity_log\
            .assert_called_once_with(user_activity_dto)
        update_user_resources_mock_object.assert_called_once_with(
            [update_resource_dto])
        update_user_club_leaderboards_mock_object.assert_called_once_with(
            user_id, user_activity_dto.resource_value,
            user_activity_dto.resource_name_enum)
        is_activity_groups_enabled_for_users_mock_object\
            .assert_called_once_with([user_id])
        update_associations_completion_metrics_of_type_activity_mock_object\
            .assert_called_once_with(user_activity_dto)

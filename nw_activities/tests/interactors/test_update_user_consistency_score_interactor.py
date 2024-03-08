import pytest

from nw_activities.interactors.update_user_consistency_score import (
    UpdateUserConsistencyScoreInteractor)
from nw_activities.tests.common_fixtures.adapters import (
    update_user_resources_mock, is_streak_enabled_mock)
from nw_activities.adapters.resources_service_adapter import \
    UpdateUserResourceDTO
from nw_activities.constants.enum import ResourceNameEnum, TransactionTypeEnum
from nw_activities.constants.constants import ACTIVITY_ID_FOR_MANUAL_UPDATION
from nw_activities.exceptions.custom_exceptions import (
    UserDoesNotHaveGamificationAccess)


class TestUpdateUserConsistencyScoreInteractor:

    def test_for_positive_value(self, mocker):
        # Arrange
        user_id = "user_1"
        resource_value = 10
        update_user_resources_mock_object = update_user_resources_mock(mocker)
        user_validation_mock_object = is_streak_enabled_mock(mocker)
        user_validation_mock_object.return_value = True
        interactor = UpdateUserConsistencyScoreInteractor()

        # Act
        interactor.update_user_consistency_score(user_id, resource_value)

        # Assert
        user_validation_mock_object.assert_called_once_with(user_id)
        update_user_resources_mock_object.assert_called_once_with(
            [UpdateUserResourceDTO(
                user_id=user_id,
                activity_id=ACTIVITY_ID_FOR_MANUAL_UPDATION,
                name_enum=ResourceNameEnum.CONSISTENCY_SCORE.value,
                value=resource_value,
                transaction_type=TransactionTypeEnum.CREDIT.value,
                entity_id=None,
                entity_type=None,
            )])

    def test_for_negative_value(self, mocker):
        # Arrange
        user_id = "user_1"
        resource_value = -10
        update_user_resources_mock_object = update_user_resources_mock(mocker)
        user_validation_mock_object = is_streak_enabled_mock(mocker)
        user_validation_mock_object.return_value = True
        interactor = UpdateUserConsistencyScoreInteractor()

        # Act
        interactor.update_user_consistency_score(user_id, resource_value)

        # Assert
        user_validation_mock_object.assert_called_once_with(user_id)
        update_user_resources_mock_object.assert_called_once_with(
            [UpdateUserResourceDTO(
                user_id=user_id,
                activity_id=ACTIVITY_ID_FOR_MANUAL_UPDATION,
                name_enum=ResourceNameEnum.CONSISTENCY_SCORE.value,
                value=abs(resource_value),
                transaction_type=TransactionTypeEnum.DEBIT.value,
                entity_id=None,
                entity_type=None,
            )])

    def test_for_invalid_user(self, mocker):
        # Arrange
        user_id = "user_1"
        resource_value = 10
        update_user_resources_mock_object = update_user_resources_mock(mocker)
        user_validation_mock_object = is_streak_enabled_mock(mocker)
        user_validation_mock_object.return_value = False
        interactor = UpdateUserConsistencyScoreInteractor()

        # Act
        with pytest.raises(UserDoesNotHaveGamificationAccess):
            interactor.update_user_consistency_score(user_id, resource_value)
        user_validation_mock_object.assert_called_once_with(user_id)
        update_user_resources_mock_object.assert_not_called()

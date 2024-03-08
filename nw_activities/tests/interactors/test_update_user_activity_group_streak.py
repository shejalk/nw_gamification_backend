import datetime
import uuid
from unittest.mock import call

import freezegun
import pytest

from nw_activities.constants.enum import ResourceNameEnum, FrequencyTypeEnum, \
    FrequencyPeriodEnum, InstanceTypeEnum, TransactionTypeEnum, \
    ResourceEntityTypeEnum, CompletionStatusEnum
from nw_activities.tests.common_fixtures.adapters import \
    update_user_resource_with_transaction_mock, get_user_resource_mock, \
    send_activity_group_streak_updated_event_mock, \
    send_activity_group_streak_updated_ws_event_mock, \
    send_user_consistency_score_updated_event_mock, \
    update_leaderboard_for_streak_change_mock, \
    send_user_consistency_score_credited_event_mock
from nw_activities.tests.common_fixtures.interactors import \
    update_activity_groups_optional_metrics_mock
from nw_activities.tests.common_fixtures.utils import generate_uuid_mock
from nw_activities.tests.factories.adapter_dtos import \
    UpdateUserResourceDTOFactory, UserResourceDTOFactory
from nw_activities.tests.factories.interactor_dtos import \
    UserActivityDTOFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupFrequencyConfigDTOFactory, \
    UserActivityGroupInstanceDTOFactory, ActivityGroupAssociationDTOFactory, \
    ActivityGroupInstanceIdentifierDTOFactory, \
    ActivityGroupOptionalMetricDTOFactory, UserActivityGroupStreakDTOFactory


@freezegun.freeze_time("2022-07-13 23:59:59")
@pytest.mark.django_db
class TestUpdateUserActivityGroupStreakInteractor:

    @pytest.fixture()
    def common_setup(self):
        from unittest.mock import create_autospec
        from nw_activities.interactors.storage_interfaces. \
            activity_group_storage_interface import \
            ActivityGroupStorageInterface
        from nw_activities.interactors.update_user_activity_group_streak \
            import UpdateUserActivityGroupStreakInteractor

        activity_group_storage_mock = create_autospec(
            ActivityGroupStorageInterface)
        interactor = UpdateUserActivityGroupStreakInteractor(
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
        user_activity_group_instance_dtos = [
            UserActivityGroupInstanceDTOFactory(
                user_id=user_id, activity_group_id=activity_group_id,
                completion_status=CompletionStatusEnum.COMPLETED.value,)
            for activity_group_id in activity_group_ids
        ]
        instance_identifiers = ["2022-07-13 08:00:00#2022-07-13 23:59:59",
                                "2022-07-13 08:00:00#2022-07-13 23:59:59"]
        uuid_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        generate_uuid_mock_object = generate_uuid_mock(mocker)
        generate_uuid_mock_object.side_effect = uuid_ids

        user_activity_group_streak_dtos = [
            UserActivityGroupStreakDTOFactory(
                id=uuid_ids[0],
                user_id=user_id,
                activity_group_id=activity_group_ids[0],
                streak_count=1,
                max_streak_count=1,
                last_updated_at=datetime.datetime(2022, 7, 13, 23, 59, 59)),
            UserActivityGroupStreakDTOFactory(
                id=uuid_ids[1],
                user_id=user_id,
                activity_group_id=activity_group_ids[1],
                streak_count=1,
                max_streak_count=1,
                last_updated_at=datetime.datetime(2022, 7, 13, 23, 59, 59)),
        ]
        activity_group_instance_identifier_dtos = [
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=activity_group_id,
                instance_identifier=instance_identifier,
            )
            for activity_group_id, instance_identifier in zip(
                activity_group_ids, instance_identifiers)
        ]
        activity_group_optional_metric_dtos = [
            ActivityGroupOptionalMetricDTOFactory(
                activity_group_id=activity_group_id)
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
        user_resource_dto = UserResourceDTOFactory(
            user_id=user_id,
            resource_name_enum=ResourceNameEnum.CONSISTENCY_SCORE.value,
        )
        update_user_resource_dtos = [
            UpdateUserResourceDTOFactory(
                 user_id=user_id,
                 name_enum=ResourceNameEnum.CONSISTENCY_SCORE.value,
                 value=1,
                 transaction_type=TransactionTypeEnum.CREDIT.value,
                 activity_id=None,
                 entity_id=str(user_activity_group_instance_dtos[0].id),
                 entity_type=ResourceEntityTypeEnum
                 .USER_ACTIVITY_GROUP_INSTANCE.value,
            ),
            UpdateUserResourceDTOFactory(
                 user_id=user_id,
                 name_enum=ResourceNameEnum.CONSISTENCY_SCORE.value,
                 value=1,
                 transaction_type=TransactionTypeEnum.CREDIT.value,
                 activity_id=None,
                 entity_id=str(user_activity_group_instance_dtos[1].id),
                 entity_type=ResourceEntityTypeEnum
                 .USER_ACTIVITY_GROUP_INSTANCE.value,
            ),
        ]

        return user_id, user_activity_dto, activity_group_association_dtos, \
            activity_group_ids, activity_group_frequency_config_dtos, \
            user_activity_group_instance_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_streak_dtos, \
            activity_group_id_wise_optional_metric_dtos, \
            user_resource_dto, update_user_resource_dtos, \
            activity_group_optional_metric_dtos

    def test_when_no_existing_ag_streak_creates_the_ag_streak(
            self, common_setup, activity_setup, mocker):
        # Arrange
        user_id, user_activity_dto, activity_group_association_dtos, \
            activity_group_ids, activity_group_frequency_config_dtos, \
            user_activity_group_instance_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_streak_dtos, \
            activity_group_id_wise_optional_metric_dtos, \
            user_resource_dto, update_user_resource_dtos, \
            activity_group_optional_metric_dtos = activity_setup

        interactor, activity_group_storage_mock = common_setup

        activity_group_storage_mock. \
            get_activity_group_associations_for_association_ids\
            .return_value = activity_group_association_dtos

        streak_related_details_dicts = [
            {'previous_consistency_score': 1, 'credit_value': 1, 'streak': 1},
            {'previous_consistency_score': 1, 'credit_value': 1, 'streak': 1},
        ]

        score_change = 2
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_user_activity_group_instances \
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_user_activity_group_streaks \
            .return_value = []
        activity_group_storage_mock.create_user_activity_group_instances \
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .return_value = activity_group_optional_metric_dtos
        update_user_resource_with_transaction_mock_object = \
            update_user_resource_with_transaction_mock(mocker)
        update_user_resource_with_transaction_mock_object.return_value = \
            [user_resource_dto]
        get_user_resource_mock_object = get_user_resource_mock(mocker)
        get_user_resource_mock_object.return_value = user_resource_dto
        update_activity_groups_optional_metrics_mock_object = \
            update_activity_groups_optional_metrics_mock(mocker)
        send_activity_group_streak_updated_ws_event_mock_object = \
            send_activity_group_streak_updated_ws_event_mock(mocker)
        send_activity_group_streak_updated_event_mock_object = \
            send_activity_group_streak_updated_event_mock(mocker)
        send_user_consistency_score_updated_event_mock_object = \
            send_user_consistency_score_updated_event_mock(mocker)
        send_user_consistency_score_credited_event_mock_object = \
            send_user_consistency_score_credited_event_mock(mocker)
        update_leaderboard_for_streak_change_mock_object = \
            update_leaderboard_for_streak_change_mock(mocker)

        # Act
        interactor.update_user_activity_group_streak_based_on_activity(
            user_activity_dto)

        # Assert
        activity_group_storage_mock \
            .get_activity_group_associations_for_association_ids \
            .assert_called_once_with([user_activity_dto.activity_name_enum])
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_user_activity_group_streaks \
            .assert_called_once_with(user_id, activity_group_ids)
        activity_group_streak_call_args = \
            activity_group_storage_mock.create_user_activity_groups_streak \
            .call_args
        for dto in user_activity_group_streak_dtos:
            assert dto in activity_group_streak_call_args[0][0]
        activity_group_storage_mock.get_user_activity_group_instances \
            .assert_called_once_with(
                user_id, activity_group_instance_identifier_dtos)
        activity_group_storage_mock.update_user_activity_groups_streak \
            .assert_not_called()
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .assert_called_once_with(activity_group_ids)
        update_user_resource_with_transaction_mock_object \
            .assert_called_once_with(
                update_user_resource_dtos, [user_resource_dto])
        get_user_resource_mock_object.assert_called_once_with(
            user_id, ResourceNameEnum.CONSISTENCY_SCORE.value)
        activity_groups_optional_metrics_call_args_list = \
            update_activity_groups_optional_metrics_mock_object \
            .call_args_list
        assert activity_groups_optional_metrics_call_args_list == [
            call(
                activity_group_id_wise_optional_metric_dtos={
                    activity_group_ids[0]:
                        activity_group_id_wise_optional_metric_dtos[
                            activity_group_ids[0]],
                },
                entity_id=ResourceNameEnum.CONSISTENCY_SCORE.value,
                entity_value=1,
                user_activity_group_instance_dtos=[
                    user_activity_group_instance_dtos[0]],
            ),
            call(
                activity_group_id_wise_optional_metric_dtos={
                    activity_group_ids[1]:
                        activity_group_id_wise_optional_metric_dtos[
                            activity_group_ids[1]],
                },
                entity_id=ResourceNameEnum.CONSISTENCY_SCORE.value,
                entity_value=1,
                user_activity_group_instance_dtos=[
                    user_activity_group_instance_dtos[1]],
            ),
        ]
        streaks = [1, 1]
        expected_args_list = [call(user_id, streaks[0]),
                              call(user_id, streaks[1])]
        ag_streak_updated_call_args_list = \
            send_activity_group_streak_updated_event_mock_object \
            .call_args_list
        for expected_args in expected_args_list:
            assert expected_args in ag_streak_updated_call_args_list
        expected_args_list = [call(user_id, activity_group_ids[0], streaks[0]),
                              call(user_id, activity_group_ids[1], streaks[1])]
        ag_streak_updated_ws_call_args_list = \
            send_activity_group_streak_updated_ws_event_mock_object \
            .call_args_list
        for expected_args in expected_args_list:
            assert expected_args in ag_streak_updated_ws_call_args_list
        expected_args_list = [call(user_id, 1), call(user_id, 1)]
        call_args_list = \
            send_user_consistency_score_updated_event_mock_object \
            .call_args_list
        for expected_args in expected_args_list:
            assert expected_args in call_args_list
        call_args_list = (
            send_user_consistency_score_credited_event_mock_object
            .call_args_list)
        assert call_args_list == [
            call(user_id, streak_related_details_dicts[0]),
            call(user_id, streak_related_details_dicts[1]),
        ]
        update_leaderboard_for_streak_change_mock_object \
            .assert_called_once_with(user_id, score_change, None)

    def test_when_existing_ag_streak_updates_the_ag_streak(
            self, common_setup, activity_setup, mocker):
        # Arrange
        user_id, user_activity_dto, activity_group_association_dtos, \
            activity_group_ids, activity_group_frequency_config_dtos, \
            user_activity_group_instance_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_streak_dtos, \
            activity_group_id_wise_optional_metric_dtos, \
            user_resource_dto, update_user_resource_dtos, \
            activity_group_optional_metric_dtos = activity_setup

        interactor, activity_group_storage_mock = common_setup

        for user_activity_group_streak_dto in user_activity_group_streak_dtos:
            user_activity_group_streak_dto.last_updated_at = \
                datetime.datetime(2022, 7, 10, 23, 59, 59)
        for update_user_resource_dto in update_user_resource_dtos:
            update_user_resource_dto.value = 2

        streak_related_details_dicts = [
            {'previous_consistency_score': 1, 'credit_value': 2, 'streak': 2},
            {'previous_consistency_score': 1, 'credit_value': 2, 'streak': 2},
        ]

        score_change = 4
        activity_group_storage_mock. \
            get_activity_group_associations_for_association_ids.return_value \
            = activity_group_association_dtos
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_user_activity_group_instances \
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_user_activity_group_streaks \
            .return_value = user_activity_group_streak_dtos
        activity_group_storage_mock.create_user_activity_group_instances \
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .return_value = activity_group_optional_metric_dtos
        update_user_resource_with_transaction_mock_object = \
            update_user_resource_with_transaction_mock(mocker)
        update_user_resource_with_transaction_mock_object.return_value = \
            [user_resource_dto]
        get_user_resource_mock_object = get_user_resource_mock(mocker)
        get_user_resource_mock_object.return_value = user_resource_dto
        update_activity_groups_optional_metrics_mock_object = \
            update_activity_groups_optional_metrics_mock(mocker)
        send_activity_group_streak_updated_ws_event_mock_object = \
            send_activity_group_streak_updated_ws_event_mock(mocker)
        send_activity_group_streak_updated_event_mock_object = \
            send_activity_group_streak_updated_event_mock(mocker)
        send_user_consistency_score_updated_event_mock_object = \
            send_user_consistency_score_updated_event_mock(mocker)
        send_user_consistency_score_credited_event_mock_object = \
            send_user_consistency_score_credited_event_mock(mocker)
        update_leaderboard_for_streak_change_mock_object = \
            update_leaderboard_for_streak_change_mock(mocker)

        # Act
        interactor.update_user_activity_group_streak_based_on_activity(
            user_activity_dto)

        # Assert
        activity_group_storage_mock \
            .get_activity_group_associations_for_association_ids \
            .assert_called_once_with([user_activity_dto.activity_name_enum])
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_user_activity_group_streaks \
            .assert_called_once_with(user_id, activity_group_ids)
        activity_group_storage_mock.create_user_activity_groups_streak \
            .assert_not_called()
        activity_group_storage_mock.get_user_activity_group_instances \
            .assert_called_once_with(
                user_id, activity_group_instance_identifier_dtos)
        activity_group_streak_call_args = \
            activity_group_storage_mock.update_user_activity_groups_streak \
            .call_args
        for dto in user_activity_group_streak_dtos:
            assert dto in activity_group_streak_call_args[0][0]
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .assert_called_once_with(activity_group_ids)
        update_user_resource_with_transaction_mock_object \
            .assert_called_once_with(
                update_user_resource_dtos, [user_resource_dto])
        get_user_resource_mock_object.assert_called_once_with(
            user_id, ResourceNameEnum.CONSISTENCY_SCORE.value)

        activity_groups_optional_metrics_call_args_list = \
            update_activity_groups_optional_metrics_mock_object \
            .call_args_list
        assert activity_groups_optional_metrics_call_args_list == [
            call(
                activity_group_id_wise_optional_metric_dtos={
                    activity_group_ids[0]:
                        activity_group_id_wise_optional_metric_dtos[
                            activity_group_ids[0]],
                },
                entity_id=ResourceNameEnum.CONSISTENCY_SCORE.value,
                entity_value=2,
                user_activity_group_instance_dtos=[
                    user_activity_group_instance_dtos[0]],
            ),
            call(
                activity_group_id_wise_optional_metric_dtos={
                    activity_group_ids[1]:
                        activity_group_id_wise_optional_metric_dtos[
                            activity_group_ids[1]],
                },
                entity_id=ResourceNameEnum.CONSISTENCY_SCORE.value,
                entity_value=2,
                user_activity_group_instance_dtos=[
                    user_activity_group_instance_dtos[1]],
            ),
        ]
        streaks = [2, 2]
        expected_args_list = [call(user_id, streaks[0]),
                              call(user_id, streaks[1])]
        ag_streak_updated_call_args_list = \
            send_activity_group_streak_updated_event_mock_object.call_args_list
        for expected_args in expected_args_list:
            assert expected_args in \
                   ag_streak_updated_call_args_list
        expected_args_list = [call(user_id, activity_group_ids[0], streaks[0]),
                              call(user_id, activity_group_ids[1], streaks[1])]
        ag_streak_updated_ws_call_args_list = \
            send_activity_group_streak_updated_ws_event_mock_object \
            .call_args_list
        for expected_args in expected_args_list:
            assert expected_args in ag_streak_updated_ws_call_args_list

        expected_args_list = [call(user_id, 1), call(user_id, 1)]
        call_args_list = \
            send_user_consistency_score_updated_event_mock_object \
            .call_args_list
        for expected_args in expected_args_list:
            assert expected_args in call_args_list
        call_args_list = (
            send_user_consistency_score_credited_event_mock_object
            .call_args_list)
        assert call_args_list == [
            call(user_id, streak_related_details_dicts[0]),
            call(user_id, streak_related_details_dicts[1]),
        ]
        update_leaderboard_for_streak_change_mock_object \
            .assert_called_once_with(user_id, score_change, None)

    def test_when_streak_last_updated_at_is_same_as_current_date(
            self, common_setup, activity_setup, mocker):
        # Arrange
        user_id, user_activity_dto, activity_group_association_dtos, \
            activity_group_ids, activity_group_frequency_config_dtos, \
            user_activity_group_instance_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_streak_dtos, \
            _, user_resource_dto, _, \
            activity_group_optional_metric_dtos = activity_setup

        interactor, activity_group_storage_mock = common_setup

        activity_group_storage_mock. \
            get_activity_group_associations_for_association_ids.return_value \
            = activity_group_association_dtos
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_user_activity_group_instances \
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_user_activity_group_streaks \
            .return_value = user_activity_group_streak_dtos
        activity_group_storage_mock.create_user_activity_group_instances \
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .return_value = activity_group_optional_metric_dtos
        update_user_resource_with_transaction_mock_object = \
            update_user_resource_with_transaction_mock(mocker)
        get_user_resource_mock_object = get_user_resource_mock(mocker)
        get_user_resource_mock_object.return_value = user_resource_dto
        update_user_resource_with_transaction_mock_object.return_value = \
            [user_resource_dto]
        update_activity_groups_optional_metrics_mock_object = \
            update_activity_groups_optional_metrics_mock(mocker)
        send_activity_group_streak_updated_ws_event_mock_object = \
            send_activity_group_streak_updated_ws_event_mock(mocker)
        send_activity_group_streak_updated_event_mock_object = \
            send_activity_group_streak_updated_event_mock(mocker)
        send_user_consistency_score_updated_event_mock_object = \
            send_user_consistency_score_updated_event_mock(mocker)
        send_user_consistency_score_credited_event_mock_object = \
            send_user_consistency_score_credited_event_mock(mocker)
        update_leaderboard_for_streak_change_mock_object = \
            update_leaderboard_for_streak_change_mock(mocker)

        # Act
        interactor.update_user_activity_group_streak_based_on_activity(
            user_activity_dto)

        # Assert
        activity_group_storage_mock \
            .get_activity_group_associations_for_association_ids \
            .assert_called_once_with([user_activity_dto.activity_name_enum])
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_user_activity_group_streaks \
            .assert_called_once_with(user_id, activity_group_ids)
        activity_group_storage_mock.create_user_activity_groups_streak \
            .assert_not_called()
        activity_group_storage_mock.get_user_activity_group_instances \
            .assert_called_once_with(
                user_id, activity_group_instance_identifier_dtos)
        activity_group_storage_mock.update_user_activity_groups_streak \
            .assert_not_called()
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .assert_not_called()
        update_user_resource_with_transaction_mock_object \
            .assert_not_called()
        get_user_resource_mock_object.assert_not_called()
        activity_groups_optional_metrics_call_args_list = \
            update_activity_groups_optional_metrics_mock_object \
            .call_args_list
        assert activity_groups_optional_metrics_call_args_list == []
        send_activity_group_streak_updated_event_mock_object \
            .assert_not_called()
        send_activity_group_streak_updated_ws_event_mock_object\
            .assert_not_called()
        send_user_consistency_score_updated_event_mock_object \
            .assert_not_called()
        send_user_consistency_score_credited_event_mock_object \
            .assert_not_called()
        update_leaderboard_for_streak_change_mock_object \
            .assert_not_called()

    @pytest.mark.parametrize(
        "instance_type", [InstanceTypeEnum.PAUSED.value,
                          InstanceTypeEnum.LEISURE.value,
                          InstanceTypeEnum.FREEZE.value],
    )
    def test_when_instance_type_is_liesure_and_paused(
            self, common_setup, activity_setup, mocker, instance_type):
        # Arrange
        user_id, user_activity_dto, activity_group_association_dtos, \
            activity_group_ids, activity_group_frequency_config_dtos, \
            user_activity_group_instance_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_streak_dtos, \
            activity_group_id_wise_optional_metric_dtos, \
            user_resource_dto, update_user_resource_dtos, \
            activity_group_optional_metric_dtos = activity_setup

        interactor, activity_group_storage_mock = common_setup

        for user_activity_group_streak_dto in user_activity_group_streak_dtos:
            user_activity_group_streak_dto.last_updated_at = \
                datetime.datetime(2022, 7, 10, 23, 59, 59)
        for user_activity_group_instance_dto in \
                user_activity_group_instance_dtos:
            user_activity_group_instance_dto.instance_type = instance_type

        streak_related_details_dicts = [
            {'previous_consistency_score': 1, 'credit_value': 1, 'streak': 1},
            {'previous_consistency_score': 1, 'credit_value': 1, 'streak': 1},
        ]

        score_change = 2
        activity_group_storage_mock. \
            get_activity_group_associations_for_association_ids.return_value \
            = activity_group_association_dtos
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_user_activity_group_instances \
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_user_activity_group_streaks \
            .return_value = user_activity_group_streak_dtos
        activity_group_storage_mock.create_user_activity_group_instances \
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .return_value = activity_group_optional_metric_dtos
        update_user_resource_with_transaction_mock_object = \
            update_user_resource_with_transaction_mock(mocker)
        update_user_resource_with_transaction_mock_object.return_value = \
            [user_resource_dto]
        send_user_consistency_score_updated_event_mock_object = \
            send_user_consistency_score_updated_event_mock(mocker)
        get_user_resource_mock_object = get_user_resource_mock(mocker)
        get_user_resource_mock_object.return_value = user_resource_dto
        update_activity_groups_optional_metrics_mock_object = \
            update_activity_groups_optional_metrics_mock(mocker)
        send_activity_group_streak_updated_ws_event_mock_object = \
            send_activity_group_streak_updated_ws_event_mock(mocker)
        send_activity_group_streak_updated_event_mock_object = \
            send_activity_group_streak_updated_event_mock(mocker)
        send_user_consistency_score_credited_event_mock_object = \
            send_user_consistency_score_credited_event_mock(mocker)
        update_leaderboard_for_streak_change_mock_object = \
            update_leaderboard_for_streak_change_mock(mocker)

        # Act
        interactor.update_user_activity_group_streak_based_on_activity(
            user_activity_dto)

        # Assert
        activity_group_storage_mock \
            .get_activity_group_associations_for_association_ids \
            .assert_called_once_with([user_activity_dto.activity_name_enum])
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_user_activity_group_streaks \
            .assert_called_once_with(user_id, activity_group_ids)
        activity_group_storage_mock.create_user_activity_groups_streak \
            .assert_not_called()
        activity_group_storage_mock.get_user_activity_group_instances \
            .assert_called_once_with(
                user_id, activity_group_instance_identifier_dtos)
        update_user_resource_with_transaction_mock_object \
            .assert_called_once_with(
                update_user_resource_dtos, [user_resource_dto])
        activity_groups_optional_metrics_call_args_list = \
            update_activity_groups_optional_metrics_mock_object \
            .call_args_list
        assert activity_groups_optional_metrics_call_args_list == [
            call(
                activity_group_id_wise_optional_metric_dtos={
                    activity_group_ids[0]:
                        activity_group_id_wise_optional_metric_dtos[
                            activity_group_ids[0]],
                },
                entity_id=ResourceNameEnum.CONSISTENCY_SCORE.value,
                entity_value=1,
                user_activity_group_instance_dtos=[
                    user_activity_group_instance_dtos[0]],
            ),
            call(
                activity_group_id_wise_optional_metric_dtos={
                    activity_group_ids[1]:
                        activity_group_id_wise_optional_metric_dtos[
                            activity_group_ids[1]],
                },
                entity_id=ResourceNameEnum.CONSISTENCY_SCORE.value,
                entity_value=1,
                user_activity_group_instance_dtos=[
                    user_activity_group_instance_dtos[1]],
            ),
        ]
        streaks = [1, 1]
        expected_args_list = [[call(user_id, activity_group_ids[0], streaks[0])],
                              [call(user_id, activity_group_ids[1], streaks[0])]]
        call_args_list = \
            send_activity_group_streak_updated_ws_event_mock_object\
            .call_args_list
        for expected_args in expected_args_list:
            assert expected_args in call_args_list
        expected_args_list = [[call(user_id, streaks[0])],
                              [call(user_id, streaks[0])]]
        ag_streak_updated_call_args_list = \
            send_activity_group_streak_updated_event_mock_object.call_args_list
        for expected_args in expected_args_list:
            assert expected_args in ag_streak_updated_call_args_list
        expected_args_list = [call(user_id, 1), call(user_id, 1)]
        call_args_list = \
            send_user_consistency_score_updated_event_mock_object \
            .call_args_list
        for expected_args in expected_args_list:
            assert expected_args in call_args_list

        call_args_list = (
            send_user_consistency_score_credited_event_mock_object
            .call_args_list)
        assert call_args_list == [
            call(user_id, streak_related_details_dicts[0]),
            call(user_id, streak_related_details_dicts[1]),
        ]
        update_leaderboard_for_streak_change_mock_object \
            .assert_called_once_with(user_id, score_change, None)

    def test_when_instance_type_is_no_activity(   #pylint: disable=R0915
            self, common_setup, activity_setup, mocker):
        # Arrange
        user_id, user_activity_dto, activity_group_association_dtos, \
            activity_group_ids, activity_group_frequency_config_dtos, \
            user_activity_group_instance_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_streak_dtos, \
            activity_group_id_wise_optional_metric_dtos, \
            user_resource_dto, update_user_resource_dtos, \
            activity_group_optional_metric_dtos = activity_setup

        interactor, activity_group_storage_mock = common_setup

        for user_activity_group_streak_dto in user_activity_group_streak_dtos:
            user_activity_group_streak_dto.last_updated_at = \
                datetime.datetime(2022, 7, 10, 23, 59, 59)
        for user_activity_group_instance_dto in \
                user_activity_group_instance_dtos:
            user_activity_group_instance_dto.instance_type = \
                InstanceTypeEnum.NO_ACTIVITY.value

        user_activity_group_streak_dtos[1].streak_count = -1
        update_user_resource_dtos[0].value = 0
        update_user_resource_dtos[1].value = 1
        update_user_resource_dtos[1].transaction_type = \
            TransactionTypeEnum.DEBIT.value

        streak_related_details_dicts = [
            {'previous_consistency_score': 1, 'credit_value': 0, 'streak': 0},
        ]

        score_change = -1
        activity_group_storage_mock. \
            get_activity_group_associations_for_association_ids.return_value \
            = activity_group_association_dtos
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_user_activity_group_instances \
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_user_activity_group_streaks \
            .return_value = user_activity_group_streak_dtos
        activity_group_storage_mock.create_user_activity_group_instances \
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .return_value = activity_group_optional_metric_dtos
        update_user_resource_with_transaction_mock_object = \
            update_user_resource_with_transaction_mock(mocker)
        get_user_resource_mock_object = get_user_resource_mock(mocker)
        get_user_resource_mock_object.return_value = user_resource_dto
        update_user_resource_with_transaction_mock_object.return_value = \
            [user_resource_dto]
        update_activity_groups_optional_metrics_mock_object = \
            update_activity_groups_optional_metrics_mock(mocker)
        send_activity_group_streak_updated_ws_event_mock_object = \
            send_activity_group_streak_updated_ws_event_mock(mocker)
        send_activity_group_streak_updated_event_mock_object = \
            send_activity_group_streak_updated_event_mock(mocker)
        send_user_consistency_score_updated_event_mock_object = \
            send_user_consistency_score_updated_event_mock(mocker)
        send_user_consistency_score_credited_event_mock_object = \
            send_user_consistency_score_credited_event_mock(mocker)
        update_leaderboard_for_streak_change_mock_object = \
            update_leaderboard_for_streak_change_mock(mocker)

        # Act
        interactor.update_user_activity_group_streak_based_on_activity(
            user_activity_dto)

        # Assert
        activity_group_storage_mock \
            .get_activity_group_associations_for_association_ids \
            .assert_called_once_with([user_activity_dto.activity_name_enum])
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_user_activity_group_streaks \
            .assert_called_once_with(user_id, activity_group_ids)

        activity_group_storage_mock.create_user_activity_groups_streak \
            .assert_not_called()
        activity_group_storage_mock.get_user_activity_group_instances \
            .assert_called_once_with(
                user_id, activity_group_instance_identifier_dtos)
        activity_group_streak_call_args = \
            activity_group_storage_mock.update_user_activity_groups_streak \
            .call_args
        for dto in user_activity_group_streak_dtos:
            assert dto in activity_group_streak_call_args[0][0]
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .assert_called_once_with(activity_group_ids)
        update_user_resource_with_transaction_mock_object \
            .assert_called_once_with(update_user_resource_dtos,
                                     [user_resource_dto])
        get_user_resource_mock_object.assert_called_once_with(
            user_id, ResourceNameEnum.CONSISTENCY_SCORE.value)

        activity_groups_optional_metrics_call_args_list = \
            update_activity_groups_optional_metrics_mock_object \
            .call_args_list
        assert activity_groups_optional_metrics_call_args_list == [
            call(
                activity_group_id_wise_optional_metric_dtos={
                    activity_group_ids[0]:
                        activity_group_id_wise_optional_metric_dtos[
                            activity_group_ids[0]],
                },
                entity_id=ResourceNameEnum.CONSISTENCY_SCORE.value,
                entity_value=0,
                user_activity_group_instance_dtos=[
                    user_activity_group_instance_dtos[0]],
            ),
            call(
                activity_group_id_wise_optional_metric_dtos={
                    activity_group_ids[1]:
                        activity_group_id_wise_optional_metric_dtos[
                            activity_group_ids[1]],
                },
                entity_id=ResourceNameEnum.CONSISTENCY_SCORE.value,
                entity_value=-1,
                user_activity_group_instance_dtos=[
                    user_activity_group_instance_dtos[1]],
            ),
        ]
        streaks = [0, 0]
        expected_args_list = [[call(user_id, streaks[0])],
                              [call(user_id, streaks[0])]]
        ag_streak_updated_call_args_list = \
            send_activity_group_streak_updated_event_mock_object.call_args_list
        for expected_args in expected_args_list:
            assert expected_args in \
                   ag_streak_updated_call_args_list
        send_activity_group_streak_updated_ws_event_mock_object\
            .assert_not_called()

        expected_args_list = [call(user_id, 1), call(user_id, 0.0)]
        call_args_list = \
            send_user_consistency_score_updated_event_mock_object \
            .call_args_list
        for expected_args in expected_args_list:
            assert expected_args in call_args_list

        call_args_list = (
            send_user_consistency_score_credited_event_mock_object
            .call_args_list)
        assert call_args_list == [
            call(user_id, streak_related_details_dicts[0])
        ]
        update_leaderboard_for_streak_change_mock_object \
            .assert_called_once_with(user_id, score_change, None)

    def test_when_existing_ag_streak_is_negative_with_no_activity( #pylint: disable=R0915
            self, common_setup, activity_setup, mocker):
        user_id, user_activity_dto, activity_group_association_dtos, \
            activity_group_ids, activity_group_frequency_config_dtos, \
            user_activity_group_instance_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_streak_dtos, \
            activity_group_id_wise_optional_metric_dtos, \
            user_resource_dto, update_user_resource_dtos, \
            activity_group_optional_metric_dtos = activity_setup

        interactor, activity_group_storage_mock = common_setup

        for user_activity_group_streak_dto in user_activity_group_streak_dtos:
            user_activity_group_streak_dto.last_updated_at = \
                datetime.datetime(2022, 7, 10, 23, 59, 59)
        for user_activity_group_instance_dto in \
                user_activity_group_instance_dtos:
            user_activity_group_instance_dto.instance_type = \
                InstanceTypeEnum.NO_ACTIVITY.value

        user_resource_dto.final_value = 11000

        user_activity_group_streak_dtos[1].streak_count = -1
        update_user_resource_dtos[0].value = 0
        update_user_resource_dtos[1].value = 200
        update_user_resource_dtos[1].transaction_type = \
            TransactionTypeEnum.DEBIT.value

        streak_related_details_dicts = [
            {'previous_consistency_score': 11000, 'credit_value': 0, 'streak': 0}]

        score_change = -200
        activity_group_storage_mock. \
            get_activity_group_associations_for_association_ids\
            .return_value = activity_group_association_dtos
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_user_activity_group_instances \
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_user_activity_group_streaks \
            .return_value = user_activity_group_streak_dtos
        activity_group_storage_mock.create_user_activity_group_instances \
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .return_value = activity_group_optional_metric_dtos
        update_user_resource_with_transaction_mock_object = \
            update_user_resource_with_transaction_mock(mocker)
        get_user_resource_mock_object = get_user_resource_mock(mocker)
        get_user_resource_mock_object.return_value = user_resource_dto
        update_user_resource_with_transaction_mock_object.return_value = \
            [user_resource_dto]
        update_activity_groups_optional_metrics_mock_object = \
            update_activity_groups_optional_metrics_mock(mocker)
        send_activity_group_streak_updated_ws_event_mock_object = \
            send_activity_group_streak_updated_ws_event_mock(mocker)
        send_activity_group_streak_updated_event_mock_object = \
            send_activity_group_streak_updated_event_mock(mocker)
        send_user_consistency_score_updated_event_mock_object = \
            send_user_consistency_score_updated_event_mock(mocker)
        send_user_consistency_score_credited_event_mock_object = \
            send_user_consistency_score_credited_event_mock(mocker)
        update_leaderboard_for_streak_change_mock_object = \
            update_leaderboard_for_streak_change_mock(mocker)

        # Act
        interactor.update_user_activity_group_streak_based_on_activity(
            user_activity_dto)

        # Assert
        activity_group_storage_mock \
            .get_activity_group_associations_for_association_ids \
            .assert_called_once_with([user_activity_dto.activity_name_enum])
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_user_activity_group_streaks \
            .assert_called_once_with(user_id, activity_group_ids)

        activity_group_storage_mock.create_user_activity_groups_streak \
            .assert_not_called()
        activity_group_storage_mock.get_user_activity_group_instances \
            .assert_called_once_with(
                user_id, activity_group_instance_identifier_dtos)
        activity_group_streak_call_args = \
            activity_group_storage_mock.update_user_activity_groups_streak \
            .call_args
        for dto in user_activity_group_streak_dtos:
            assert dto in activity_group_streak_call_args[0][0]
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .assert_called_once_with(activity_group_ids)
        update_user_resource_with_transaction_mock_object \
            .assert_called_once_with(update_user_resource_dtos,
                                     [user_resource_dto])
        get_user_resource_mock_object.assert_called_once_with(
            user_id, ResourceNameEnum.CONSISTENCY_SCORE.value)

        activity_groups_optional_metrics_call_args_list = \
            update_activity_groups_optional_metrics_mock_object \
            .call_args_list
        assert activity_groups_optional_metrics_call_args_list == [
            call(
                activity_group_id_wise_optional_metric_dtos={
                    activity_group_ids[0]:
                        activity_group_id_wise_optional_metric_dtos[
                            activity_group_ids[0]],
                },
                entity_id=ResourceNameEnum.CONSISTENCY_SCORE.value,
                entity_value=0,
                user_activity_group_instance_dtos=[
                    user_activity_group_instance_dtos[0]],
            ),
            call(
                activity_group_id_wise_optional_metric_dtos={
                    activity_group_ids[1]:
                        activity_group_id_wise_optional_metric_dtos[
                            activity_group_ids[1]],
                },
                entity_id=ResourceNameEnum.CONSISTENCY_SCORE.value,
                entity_value=-200,
                user_activity_group_instance_dtos=[
                    user_activity_group_instance_dtos[1]],
            ),
        ]
        expected_args_list = [[call(user_id, 0)],
                              [call(user_id, 0)]]
        ag_streak_updated_call_args_list = \
            send_activity_group_streak_updated_event_mock_object.call_args_list
        for expected_args in expected_args_list:
            assert expected_args in \
                   ag_streak_updated_call_args_list
        send_activity_group_streak_updated_ws_event_mock_object \
            .assert_not_called()

        expected_args_list = [
            call(user_id, 10800), call(user_id, 11000)]
        call_args_list = \
            send_user_consistency_score_updated_event_mock_object \
            .call_args_list
        for expected_args in expected_args_list:
            assert expected_args in call_args_list

        call_args_list = (
            send_user_consistency_score_credited_event_mock_object
            .call_args_list)
        assert call_args_list == [
            call(user_id, streak_related_details_dicts[0])
        ]
        update_leaderboard_for_streak_change_mock_object \
            .assert_called_once_with(user_id, score_change, None)

    def test_when_existing_ag_streak_is_negative_with_activity(
            self, common_setup, activity_setup, mocker):
        # Arrange
        user_id, user_activity_dto, activity_group_association_dtos, \
            activity_group_ids, activity_group_frequency_config_dtos, \
            user_activity_group_instance_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_streak_dtos, \
            activity_group_id_wise_optional_metric_dtos, \
            user_resource_dto, update_user_resource_dtos, \
            activity_group_optional_metric_dtos = activity_setup

        interactor, activity_group_storage_mock = common_setup

        for user_activity_group_streak_dto in user_activity_group_streak_dtos:
            user_activity_group_streak_dto.last_updated_at = \
                datetime.datetime(2022, 7, 10, 23, 59, 59)
            user_activity_group_streak_dto.streak_count = -2

        streak_related_details_dicts = [
            {'previous_consistency_score': 1, 'credit_value': 1, 'streak': 1},
            {'previous_consistency_score': 1, 'credit_value': 1, 'streak': 1},
        ]

        score_change = 2
        activity_group_storage_mock. \
            get_activity_group_associations_for_association_ids\
            .return_value = activity_group_association_dtos
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_user_activity_group_instances \
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_user_activity_group_streaks \
            .return_value = user_activity_group_streak_dtos
        activity_group_storage_mock.create_user_activity_group_instances \
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .return_value = activity_group_optional_metric_dtos
        update_user_resource_with_transaction_mock_object = \
            update_user_resource_with_transaction_mock(mocker)
        send_user_consistency_score_updated_event_mock_object = \
            send_user_consistency_score_updated_event_mock(mocker)

        get_user_resource_mock_object = get_user_resource_mock(mocker)
        get_user_resource_mock_object.return_value = user_resource_dto
        update_user_resource_with_transaction_mock_object.return_value = \
            [user_resource_dto]
        update_activity_groups_optional_metrics_mock_object = \
            update_activity_groups_optional_metrics_mock(mocker)
        send_activity_group_streak_updated_ws_event_mock_object = \
            send_activity_group_streak_updated_ws_event_mock(mocker)
        send_activity_group_streak_updated_event_mock_object = \
            send_activity_group_streak_updated_event_mock(mocker)
        send_user_consistency_score_credited_event_mock_object = \
            send_user_consistency_score_credited_event_mock(mocker)
        update_leaderboard_for_streak_change_mock_object = \
            update_leaderboard_for_streak_change_mock(mocker)

        # Act
        interactor.update_user_activity_group_streak_based_on_activity(
            user_activity_dto)

        # Assert
        activity_group_storage_mock \
            .get_activity_group_associations_for_association_ids \
            .assert_called_once_with([user_activity_dto.activity_name_enum])
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_user_activity_group_streaks \
            .assert_called_once_with(user_id, activity_group_ids)
        activity_group_storage_mock.create_user_activity_groups_streak\
            .assert_not_called()
        activity_group_storage_mock.get_user_activity_group_instances \
            .assert_called_once_with(
                user_id, activity_group_instance_identifier_dtos)
        activity_group_streak_call_args = \
            activity_group_storage_mock.update_user_activity_groups_streak \
            .call_args

        for dto in user_activity_group_streak_dtos:
            assert dto in activity_group_streak_call_args[0][0]
            assert dto.streak_count == 1
        activity_group_storage_mock.get_activity_groups_optional_metrics \
            .assert_called_once_with(activity_group_ids)
        update_user_resource_with_transaction_mock_object \
            .assert_called_once_with(update_user_resource_dtos,
                                     [user_resource_dto])
        get_user_resource_mock_object.assert_called_once_with(
            user_id, ResourceNameEnum.CONSISTENCY_SCORE.value)

        activity_groups_optional_metrics_call_args_list = \
            update_activity_groups_optional_metrics_mock_object \
            .call_args_list
        assert activity_groups_optional_metrics_call_args_list == [
            call(
                activity_group_id_wise_optional_metric_dtos={
                    activity_group_ids[0]:
                        activity_group_id_wise_optional_metric_dtos[
                            activity_group_ids[0]],
                },
                entity_id=ResourceNameEnum.CONSISTENCY_SCORE.value,
                entity_value=1,
                user_activity_group_instance_dtos=[
                    user_activity_group_instance_dtos[0]],
            ),
            call(
                activity_group_id_wise_optional_metric_dtos={
                    activity_group_ids[1]:
                        activity_group_id_wise_optional_metric_dtos[
                            activity_group_ids[1]],
                },
                entity_id=ResourceNameEnum.CONSISTENCY_SCORE.value,
                entity_value=1,
                user_activity_group_instance_dtos=[
                    user_activity_group_instance_dtos[1]],
            ),
        ]
        streaks = [1, 1]
        expected_args_list = [call(user_id, activity_group_ids[0], streaks[0]),
                              call(user_id, activity_group_ids[1], streaks[1])]
        ag_streak_updated_ws_call_args_list = \
            send_activity_group_streak_updated_ws_event_mock_object \
            .call_args_list
        for expected_args in expected_args_list:
            assert expected_args in ag_streak_updated_ws_call_args_list

        expected_args_list = [call(user_id, streaks[0]),
                              call(user_id, streaks[1])]
        ag_streak_updated_call_args_list = \
            send_activity_group_streak_updated_event_mock_object \
            .call_args_list
        for expected_args in expected_args_list:
            assert expected_args in ag_streak_updated_call_args_list

        expected_args_list = [call(user_id, 1), call(user_id, 1)]
        call_args_list = \
            send_user_consistency_score_updated_event_mock_object \
            .call_args_list
        for expected_args in expected_args_list:
            assert expected_args in call_args_list

        call_args_list = (
            send_user_consistency_score_credited_event_mock_object
            .call_args_list)
        assert call_args_list == [
            call(user_id, streak_related_details_dicts[0]),
            call(user_id, streak_related_details_dicts[1]),
        ]
        update_leaderboard_for_streak_change_mock_object \
            .assert_called_once_with(user_id, score_change, None)

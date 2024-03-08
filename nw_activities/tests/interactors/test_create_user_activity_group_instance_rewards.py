import uuid
import freezegun
import pytest

from nw_activities.constants.enum import FrequencyTypeEnum, \
    FrequencyPeriodEnum, RewardTypeEnum, CompletionMetricEntityTypeEnum, \
    OperatorEnum, TransactionTypeEnum, RewardEntityTypeEnum
from nw_activities.tests.common_fixtures.adapters import \
    get_reward_config_details_mock, update_user_resources_mock
from nw_activities.tests.common_fixtures.utils import generate_uuid_mock
from nw_activities.tests.factories.adapter_dtos import \
    UpdateUserResourceDTOFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupAssociationDTOFactory, \
    ActivityGroupFrequencyConfigDTOFactory,\
    ActivityGroupInstanceIdentifierDTOFactory, \
    UserActivityGroupInstanceDTOFactory, ActivityGroupRewardConfigDTOFactory, \
    ActivityGroupCompletionMetricDTOFactory, \
    UserActivityGroupInstanceMetricTrackerDTOFactory, \
    UserActivityGroupInstanceRewardDTOFactory, \
    UserAGInstanceIdAGRewardConfigIdDTOFactory
from nw_resources.tests.factories.storage_dtos import \
    RewardConfigCompleteDetailsDTOFactory


@freezegun.freeze_time("2022-07-13 23:59:59")
@pytest.mark.django_db
class TestCreateUserActivityGroupInstanceRewardInteractor:

    @pytest.fixture()
    def common_setup(self):
        from unittest.mock import create_autospec
        from nw_activities.interactors.storage_interfaces. \
            activity_group_storage_interface import \
            ActivityGroupStorageInterface
        from nw_activities.interactors. \
            create_user_activity_group_instance_rewards import \
            CreateUserActivityGroupInstanceRewardInteractor

        activity_group_storage_mock = create_autospec(
            ActivityGroupStorageInterface)
        interactor = CreateUserActivityGroupInstanceRewardInteractor(
            activity_group_storage_mock)

        return interactor, activity_group_storage_mock

    @pytest.fixture()
    def activity_setup(self, mocker):
        user_id = str(uuid.uuid4())

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
            str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()),
            str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()),
            str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()),
        ]
        generate_uuid_mock_object = generate_uuid_mock(mocker)
        generate_uuid_mock_object.side_effect = uuid_ids

        activity_group_instance_identifier_dtos = [
            ActivityGroupInstanceIdentifierDTOFactory(
                activity_group_id=activity_group_id,
                instance_identifier=instance_identifier,
            )
            for activity_group_id, instance_identifier in zip(
                activity_group_ids, instance_identifiers)
        ]
        user_activity_group_instance_dtos = [
            UserActivityGroupInstanceDTOFactory(
                user_id=user_id, activity_group_id=activity_group_id,
            )
            for activity_group_id in activity_group_ids
        ]
        activity_group_reward_config_dtos = [
            ActivityGroupRewardConfigDTOFactory(
                id=uuid_ids[0], activity_group_id=activity_group_ids[0],
                resource_reward_config_id=uuid_ids[1],
            ),
            ActivityGroupRewardConfigDTOFactory(
                id=uuid_ids[2], activity_group_id=activity_group_ids[1],
                resource_reward_config_id=uuid_ids[3],
            ),
        ]

        activity_group_completion_metric_dtos = [
            ActivityGroupCompletionMetricDTOFactory(
                id=uuid_ids[4], entity_id=uuid_ids[5],
                activity_group_id=activity_group_ids[0],
                entity_type=CompletionMetricEntityTypeEnum.RESOURCE.value,
            ),
            ActivityGroupCompletionMetricDTOFactory(
                id=uuid_ids[6], entity_id=uuid_ids[7],
                activity_group_id=activity_group_ids[1],
                entity_type=CompletionMetricEntityTypeEnum.RESOURCE.value,
            ),
        ]
        user_ag_instance_id_reward_config_id_dtos = [
            UserAGInstanceIdAGRewardConfigIdDTOFactory(
                user_activity_group_instance_id=
                user_activity_group_instance_dtos[0].id,
                activity_group_reward_config_id=
                activity_group_reward_config_dtos[0].id,
            ),
            UserAGInstanceIdAGRewardConfigIdDTOFactory(
                user_activity_group_instance_id=
                user_activity_group_instance_dtos[1].id,
                activity_group_reward_config_id=
                activity_group_reward_config_dtos[1].id,
            ),
        ]
        user_activity_group_instance_metric_tracker_dtos = [
            UserActivityGroupInstanceMetricTrackerDTOFactory(
                id=uuid_ids[8],
                user_activity_group_instance_id
                =user_activity_group_instance_dtos[0].id,
                activity_group_completion_metric_id
                =activity_group_completion_metric_dtos[0].id,
            ),
            UserActivityGroupInstanceMetricTrackerDTOFactory(
                id=uuid_ids[9], user_activity_group_instance_id
                =user_activity_group_instance_dtos[1].id,
                activity_group_completion_metric_id
                =activity_group_completion_metric_dtos[1].id,
            ),
        ]
        user_activity_group_instance_reward_dtos = [
            UserActivityGroupInstanceRewardDTOFactory(
                id=uuid_ids[10], user_activity_group_instance_id
                =user_activity_group_instance_dtos[0].id,
                activity_group_reward_config_id
                =activity_group_reward_config_dtos[0].id,
                rewarded_at_value=1,
            ),
            UserActivityGroupInstanceRewardDTOFactory(
                id=uuid_ids[11], user_activity_group_instance_id
                =user_activity_group_instance_dtos[1].id,
                activity_group_reward_config_id
                =activity_group_reward_config_dtos[1].id,
                rewarded_at_value=1,
            ),
        ]
        resource_reward_config_ids = [
            activity_group_reward_config_dtos[0].resource_reward_config_id,
            activity_group_reward_config_dtos[1].resource_reward_config_id,
        ]

        reward_config_complete_details_dtos = [
            RewardConfigCompleteDetailsDTOFactory(
                reward_config_id=resource_reward_config_ids[0],
                reward_type=RewardTypeEnum.RESOURCE_BASED.value,
                operator=OperatorEnum.GTE.value,
                value=1,
            ),
            RewardConfigCompleteDetailsDTOFactory(
                reward_config_id=resource_reward_config_ids[1],
                reward_type=RewardTypeEnum.RESOURCE_BASED.value,
                operator=OperatorEnum.GTE.value,
            ),
        ]
        name_enum = 'resource_name_enum_2'
        update_user_resource_dtos = [
            UpdateUserResourceDTOFactory(
                name_enum=name_enum,
                user_id=user_id,
                value=2, transaction_type=TransactionTypeEnum.DEBIT.value,
                activity_id=None,
                entity_id=user_activity_group_instance_dtos[1].id,
                entity_type=RewardEntityTypeEnum.USER_ACTIVITY_GROUP_INSTANCE
                .value,
            ),
        ]

        user_activity_group_instance_reward_dtos_to_create = [
            UserActivityGroupInstanceRewardDTOFactory(
                id=uuid_ids[0], user_activity_group_instance_id=
                user_activity_group_instance_dtos[1].id,
                activity_group_reward_config_id=
                activity_group_reward_config_dtos[1].id,
                rewarded_at_value=2.0,
            ),
        ]

        return user_id, activity_group_ids, activity_group_association_dtos, \
            activity_group_frequency_config_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_instance_dtos, \
            activity_group_reward_config_dtos, \
            activity_group_completion_metric_dtos, \
            user_activity_group_instance_metric_tracker_dtos, \
            user_activity_group_instance_reward_dtos, \
            user_ag_instance_id_reward_config_id_dtos, \
            resource_reward_config_ids, \
            reward_config_complete_details_dtos, update_user_resource_dtos,\
            user_activity_group_instance_reward_dtos_to_create

    def test_when_no_existing_user_agi_creates_user_agi(
            self, common_setup, activity_setup, mocker):
        # Arrange
        user_id, activity_group_ids, activity_group_association_dtos, \
            activity_group_frequency_config_dtos, \
            activity_group_instance_identifier_dtos, \
            user_activity_group_instance_dtos, \
            activity_group_reward_config_dtos, \
            activity_group_completion_metric_dtos, \
            user_activity_group_instance_metric_tracker_dtos, \
            user_activity_group_instance_reward_dtos, \
            user_ag_instance_id_reward_config_id_dtos, \
            resource_reward_config_ids, reward_config_complete_details_dtos, \
            update_user_resource_dtos, \
            user_activity_group_instance_reward_dtos_to_create\
            = activity_setup

        interactor, activity_group_storage_mock = common_setup

        activity_group_storage_mock. \
            get_activity_group_associations_for_association_ids.side_effect = \
            [activity_group_association_dtos, []]
        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .return_value = activity_group_frequency_config_dtos
        activity_group_storage_mock.get_user_activity_group_instances \
            .return_value = user_activity_group_instance_dtos
        activity_group_storage_mock.get_activity_group_reward_configs \
            .return_value = activity_group_reward_config_dtos
        activity_group_storage_mock.get_activity_groups_completion_metrics \
            .return_value = activity_group_completion_metric_dtos
        activity_group_storage_mock \
            .get_user_activity_group_instances_metric_tracker_without_transaction \
            .return_value = user_activity_group_instance_metric_tracker_dtos
        activity_group_storage_mock \
            .get_latest_user_activity_group_instance_rewards_with_transaction \
            .return_value = user_activity_group_instance_reward_dtos

        get_reward_config_details_mock_object = \
            get_reward_config_details_mock(mocker)
        get_reward_config_details_mock_object.return_value = \
            reward_config_complete_details_dtos
        update_user_resources_mock_object = update_user_resources_mock(mocker)

        # Act
        interactor.create_user_activity_group_instance_rewards(
            user_id, activity_group_ids)

        # Assert
        activity_group_associations_call_args = \
            activity_group_storage_mock \
            .get_activity_group_associations_for_association_ids.call_args

        expected_call_args = [
            [activity_group_ids[0], activity_group_ids[1]],
            [activity_group_ids[0], activity_group_ids[1]],
        ]
        for expected_call_arg in expected_call_args:
            assert expected_call_arg in \
                activity_group_associations_call_args[0]

        activity_group_storage_mock.get_activity_groups_frequency_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_user_activity_group_instances \
            .assert_called_once_with(user_id,
                                     activity_group_instance_identifier_dtos)
        activity_group_storage_mock.get_activity_group_reward_configs \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock.get_activity_groups_completion_metrics \
            .assert_called_once_with(activity_group_ids)
        activity_group_storage_mock \
            .get_user_activity_group_instances_metric_tracker_without_transaction \
            .assert_called_once_with([user_activity_group_instance_dtos[0].id,
                                      user_activity_group_instance_dtos[1].id])
        activity_group_storage_mock \
            .get_latest_user_activity_group_instance_rewards_with_transaction \
            .assert_called_once_with(user_ag_instance_id_reward_config_id_dtos)
        get_reward_config_details_mock_object.assert_called_once_with(
            resource_reward_config_ids)
        update_user_resources_mock_object.assert_called_once_with(
            update_user_resource_dtos)
        activity_group_storage_mock\
            .create_user_activity_group_instance_rewards\
            .assert_called_once_with(
                user_activity_group_instance_reward_dtos_to_create)

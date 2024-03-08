"""
# Test Case for default case
"""
import pytest
import json
from django_swagger_utils.utils.test_utils import TestUtils

from nw_activities.adapters.resources_service_adapter import UserResourceDTO, \
    UpdateUserResourceDTO
from . import APP_NAME, OPERATION_NAME, REQUEST_METHOD, URL_SUFFIX, \
    URL_BASE_PATH
from nw_activities.tests.factories.models import \
    UserActivityGroupInstanceFactory, ActivityGroupFactory, \
    ActivityGroupConfigFactory, FrequencyConfigFactory
from nw_activities.constants.enum import FrequencyTypeEnum, \
    WeekDayEnum, FrequencyPeriodEnum, CompletionStatusEnum, \
    InstanceTypeEnum, ResourceNameEnum, TransactionTypeEnum, \
    StreakFreezeActivityNameEnum
from nw_activities.tests.common_fixtures.adapters import \
    get_user_resource_mock, update_user_resources_mock


class TestCase01CreateStreakFreezeV1APITestCase(TestUtils):
    APP_NAME = APP_NAME
    URL_BASE_PATH = URL_BASE_PATH
    OPERATION_NAME = OPERATION_NAME
    REQUEST_METHOD = REQUEST_METHOD
    URL_SUFFIX = URL_SUFFIX
    SECURITY = {'oauth': {'scopes': ['read', 'write']}}
    def setupUser(self, username, password):
        pass

    @staticmethod
    def _create_custom_user(user_id: str):
        from django.contrib.auth import get_user_model
        username = 'username'
        password = 'password'
        User = get_user_model()
        user = User.objects.create_user(
            username, "%s@user.com" % username, password,
            user_id=user_id)
        return user

    def _get_or_create_user(self):
        from django.contrib.auth import get_user_model
        username = "username"
        password = "password"
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(
                user_id='4e3af0cf-c591-476a-976a-b829fd3aded8',
                username=username, email="%s@user.com" % username,
                password=password)

        return user

    @pytest.fixture
    def setup_data(self, mocker):
        user_id = '4e3af0cf-c591-476a-976a-b829fd3aded8'
        activity_group_ids = ['f0d4bd1f-be77-4db4-807a-a129404e5374',
                              '1c90eb12-81b6-4d3a-acc8-0459769d4cfb']
        user_activity_group_instance_ids = [
            '07bb5eea-3a19-44ac-8d8d-6cb5f10209ec',
            'ba971f2c-c97f-44d4-9c1e-e1f13d290cee']
        frequency_configs = [
            FrequencyConfigFactory(

                frequency_type=FrequencyTypeEnum.WEEKLY.value,
                config=json.dumps({
                    "starts_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "09:00:00"
                        },
                        {
                            "value_type": FrequencyPeriodEnum.DAY.value,
                            "value": WeekDayEnum.MONDAY.value
                        }
                    ],
                    "ends_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "21:00:00"
                        },
                        {
                            "value_type": FrequencyPeriodEnum.DAY.value,
                            "value": WeekDayEnum.SUNDAY.value
                        }
                    ]
                })
            ),
            FrequencyConfigFactory(
                frequency_type=FrequencyTypeEnum.DAILY.value,
                config=json.dumps({
                    "starts_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "07:00:00"
                        }
                    ],
                    "ends_at": [
                        {
                            "value_type": FrequencyPeriodEnum.TIME.value,
                            "value": "23:00:00"
                        }
                    ]
                })
            )
        ]
        activity_groups = [
            ActivityGroupFactory(
                id=activity_group_ids[0],
                name="activity_group_1",
                description="activity_group_1_description"
            ),
            ActivityGroupFactory(
                id=activity_group_ids[1],
                name="activity_group_2",
                description="activity_group_2_description"
            )
        ]

        activity_group_configs = [
            ActivityGroupConfigFactory(
                activity_group=activity_groups[0],
                frequency_config=frequency_configs[1],
                should_consider_for_streak=True
            ),
            ActivityGroupConfigFactory(
                activity_group=activity_groups[1],
                frequency_config=frequency_configs[0]
            )
        ]

        user_activity_group_instance_dtos = [
            UserActivityGroupInstanceFactory(
                id=user_activity_group_instance_ids[0],
                user_id=user_id,
                activity_group_id=activity_group_ids[1],
                completion_percentage=0.0,
                instance_identifier="2022-07-11 09:00:00#2022-07-17 21:00:00",
                completion_status=CompletionStatusEnum.YET_TO_START.value
            ),
            UserActivityGroupInstanceFactory(
                id=user_activity_group_instance_ids[1],
                user_id=user_id,
                activity_group_id=activity_group_ids[0],
                completion_percentage=0.0,
                instance_identifier="2022-07-13 07:00:00#2022-07-13 23:00:00",
                completion_status=CompletionStatusEnum.YET_TO_START.value,
                instance_type=InstanceTypeEnum.FREEZE.value
            )
        ]
        get_user_resources_mock_object = get_user_resource_mock(mocker)
        update_user_resources_mock_object = update_user_resources_mock(mocker)

        return get_user_resources_mock_object, update_user_resources_mock_object

    @pytest.mark.django_db
    def test_case(self, snapshot, setup_data):
        get_user_resources_mock_object, update_user_resources_mock_object \
            = setup_data
        user_id = '4e3af0cf-c591-476a-976a-b829fd3aded8'
        self.foo_user = self._get_or_create_user()
        body = {'freeze_date': '2023-12-31'}
        get_user_resources_mock_object.return_value = UserResourceDTO(
            user_id=user_id,
            resource_name_enum=ResourceNameEnum.STREAK_FREEZES.value,
            final_value=3,
            user_resource_id="user_resource_id"
        )
        update_user_resource_dtos = [
            UpdateUserResourceDTO(
                user_id=user_id,
                name_enum=ResourceNameEnum.STREAK_FREEZES.value,
                value=1,
                transaction_type=TransactionTypeEnum.DEBIT.value,
                activity_id=StreakFreezeActivityNameEnum.STREAK_FREEZE.value,
                entity_id=None,
                entity_type=None
            )
        ]
        path_params = {}
        query_params = {}
        headers = {}
        response = self.make_api_call(body=body,
                                      path_params=path_params,
                                      query_params=query_params,
                                      headers=headers,
                                      snapshot=snapshot)

        assert response.status_code == 201
        update_user_resources_mock_object.assert_called_once_with(
            update_user_resource_dtos)

import datetime
import calendar

from ib_common.date_time_utils.get_current_local_date_time import \
    get_current_local_date_time
from ib_common.decorators.atomic_transaction import atomic_transaction

from nw_activities.adapters.service_adapter import get_service_adapter
from nw_activities.adapters.resources_service_adapter import \
    UpdateUserResourceDTO
from nw_activities.constants.enum import ResourceNameEnum, InstanceTypeEnum, \
    TransactionTypeEnum, StreakFreezeActivityNameEnum
from nw_activities.exceptions.custom_exceptions import \
    InsufficientFreezeBalanceException, MonthlyFreezeLimitExceededException, \
    StreakFreezeAlreadyExistsException
from nw_activities.interactors.dtos import UserInstanceTypeDTO
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import ActivityGroupStorageInterface
from nw_activities.interactors.presenter_interfaces. \
    streak_freeze_presenter_interface import StreakFreezePresenterInterface


class CreateStreakFreezeInteractor:
    def __init__(self, activity_group_storge: ActivityGroupStorageInterface):
        self.activity_group_storage = activity_group_storge

    def create_streak_freeze_wrapper(
            self, user_id: str, instance_date: datetime.date,
            presenter: StreakFreezePresenterInterface):
        try:
            self.create_streak_freeze(user_id, instance_date)
            return presenter.get_streak_freeze_created_success_response()
        except InsufficientFreezeBalanceException as exception:
            return presenter.raise_insufficient_streak_freeze_left_exception(
                exception.freeze_balance,
            )
        except MonthlyFreezeLimitExceededException as exception:
            return presenter.raise_monthly_freeze_limit_exceeded_exception(
                exception.freezes_used_in_current_month,
                exception.maximum_freezes_allowed_per_month,
            )
        except StreakFreezeAlreadyExistsException as exception:
            return presenter.raise_streak_freeze_already_exists_exception(
                exception.instance_date,
            )

    @atomic_transaction()
    def create_streak_freeze(
            self, user_id: str, instance_date: datetime.date):
        self._validate_is_datetime_already_frozen(user_id, instance_date)
        self._validate_user_streak_freeze_balance(user_id)
        self._validate_user_monthly_streak_freeze_limit(user_id)

        self._create_streak_freeze_for_user(user_id, instance_date)

    def _validate_is_datetime_already_frozen(
            self, user_id: str, instance_date: datetime.date):
        from nw_activities.interactors. \
            get_user_activity_group_instance_details \
            import GetUserActivityGroupInstanceInteractor

        interactor = GetUserActivityGroupInstanceInteractor(
            self.activity_group_storage)
        activity_group_instances = interactor. \
            get_user_streak_activity_group_instances_for_given_dates(
                user_id, [instance_date], [InstanceTypeEnum.FREEZE.value])

        if activity_group_instances:
            raise StreakFreezeAlreadyExistsException(instance_date)

    def _validate_user_streak_freeze_balance(self, user_id: str):
        user_freeze_balance = self._get_user_streak_freezes(user_id)
        if not user_freeze_balance or user_freeze_balance <= 0:
            raise InsufficientFreezeBalanceException(user_freeze_balance)

    @staticmethod
    def _get_user_streak_freezes(user_id):
        adapter = get_service_adapter()
        user_freeze_balance = adapter.resources.get_user_resource(
            user_id, ResourceNameEnum.STREAK_FREEZES.value)
        if user_freeze_balance:
            user_freeze_balance = user_freeze_balance.final_value
        return user_freeze_balance

    def _validate_user_monthly_streak_freeze_limit(self, user_id: str):
        maximum_freezes_allowed_per_month = \
            self._get_maximum_freezes_allowed_per_month()
        freezes_used_in_current_month = \
            self._get_user_monthly_streak_freezes(user_id)
        if freezes_used_in_current_month >= \
                maximum_freezes_allowed_per_month:
            raise MonthlyFreezeLimitExceededException(
                freezes_used_in_current_month,
                maximum_freezes_allowed_per_month)

    @staticmethod
    def _get_maximum_freezes_allowed_per_month():
        adapter = get_service_adapter()
        maximum_freezes_allowed_per_month = adapter.gamification_wrapper. \
            get_maximum_number_of_streak_freezes_allowed_per_month()
        return maximum_freezes_allowed_per_month

    def _get_user_monthly_streak_freezes(self, user_id: str) -> int:
        current_datetime = get_current_local_date_time()
        current_date = current_datetime.date()
        month_start_date = current_date.replace(day=1)
        month_end_date = month_start_date.replace(
            day=calendar.monthrange(
                month_start_date.year, month_start_date.month)[1])
        user_streak_freeze_balance = self._get_user_activity_group_instances(
            user_id, month_start_date, month_end_date)
        return user_streak_freeze_balance

    def _get_user_activity_group_instances(
            self, user_id: str, start_date: datetime.date,
            end_date: datetime.date) -> int:
        from nw_activities.interactors. \
            get_user_activity_group_instance_details \
            import GetUserActivityGroupInstanceInteractor

        interactor = GetUserActivityGroupInstanceInteractor(
            self.activity_group_storage)
        activity_group_instances = interactor. \
            get_user_streak_activity_group_instances_between_given_dates(
                user_id, start_date, end_date, [InstanceTypeEnum.FREEZE.value])

        return len(activity_group_instances)

    def _create_streak_freeze_for_user(
            self, user_id: str, instance_date: datetime.date):
        from nw_activities.interactors.create_user_activity_group_instances \
            import CreateUserActivityGroupInstanceInteractor
        interactor = CreateUserActivityGroupInstanceInteractor(
            self.activity_group_storage)
        user_instance_type_dtos = [
            UserInstanceTypeDTO(
                user_id=user_id,
                instance_type=InstanceTypeEnum.FREEZE.value),
        ]

        interactor. \
            create_user_activity_group_streak_instance_with_daily_frequency(
            user_instance_type_dtos, instance_date)

        self._update_user_streak_freeze_balance(
            user_id, streak_freezes_created=1)

    @staticmethod
    def _update_user_streak_freeze_balance(
            user_id: str, streak_freezes_created: int):
        adapter = get_service_adapter()
        user_resource_dtos = [
            UpdateUserResourceDTO(
                user_id=user_id,
                name_enum=ResourceNameEnum.STREAK_FREEZES.value,
                value=streak_freezes_created,
                transaction_type=TransactionTypeEnum.DEBIT.value,
                activity_id=StreakFreezeActivityNameEnum.STREAK_FREEZE.value,
                entity_id=None,
                entity_type=None,
            ),
        ]
        adapter.resources.update_user_resources(user_resource_dtos)

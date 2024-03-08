import datetime

from nw_activities.adapters.service_adapter import get_service_adapter
from nw_activities.adapters.resources_service_adapter import \
    UpdateUserResourceDTO
from nw_activities.constants.enum import InstanceTypeEnum, ResourceNameEnum, \
    TransactionTypeEnum, StreakFreezeActivityNameEnum
from nw_activities.exceptions.custom_exceptions import \
    StreakFreezeNotFoundException
from nw_activities.interactors.presenter_interfaces.streak_freeze_presenter_interface import \
    StreakFreezePresenterInterface
from nw_activities.interactors.storage_interfaces.activity_group_storage_interface import \
    ActivityGroupStorageInterface


class CancelUserStreakFreezeInteractor:

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        self.activity_group_storage = activity_group_storage

    def cancel_user_streak_freeze_wrapper(
            self, user_id: str, instance_date: datetime.date,
            presenter: StreakFreezePresenterInterface):
        try:
            self.cancel_user_streak_freeze(user_id, instance_date)
            return presenter.get_streak_freeze_deleted_successfully_response()
        except StreakFreezeNotFoundException:
            return presenter.raise_streak_freeze_not_found_exception(
                instance_date)

    def cancel_user_streak_freeze(
            self, user_id: str, instance_date: datetime.date):
        self._validate_user_streak_freeze(user_id, instance_date)
        self._delete_user_streak_freeze(user_id, instance_date)
        self._update_user_streak_freeze_balance(user_id, 1)

    def _validate_user_streak_freeze(
            self, user_id: str, instance_date: datetime.date):
        user_activity_group_instance = \
            self._get_user_activity_group_instance(user_id, instance_date)
        if not user_activity_group_instance:
            raise StreakFreezeNotFoundException

    def _delete_user_streak_freeze(self, user_id: str,
                                   instance_date: datetime.date):
        from nw_activities.interactors.create_user_activity_group_instances \
            import CreateUserActivityGroupInstanceInteractor

        interactor = CreateUserActivityGroupInstanceInteractor(
            self.activity_group_storage)

        interactor.delete_streak_users_activity_group_instances_with_daily_frequency(
            [user_id], instance_date)

    def _get_user_activity_group_instance(
            self, user_id: str, instance_date: datetime.date):
        from nw_activities.interactors. \
            get_user_activity_group_instance_details import \
            GetUserActivityGroupInstanceInteractor

        interactor = GetUserActivityGroupInstanceInteractor(
            self.activity_group_storage)

        user_activity_group_instance = interactor. \
            get_user_streak_activity_group_instances_for_given_dates(
                user_id, [instance_date], [InstanceTypeEnum.FREEZE.value])

        return user_activity_group_instance

    @staticmethod
    def _update_user_streak_freeze_balance(
            user_id: str, streak_freezes_to_credit: int):
        adapter = get_service_adapter()
        update_user_resource_dtos = [
            UpdateUserResourceDTO(
                user_id=user_id,
                name_enum=ResourceNameEnum.STREAK_FREEZES.value,
                value=streak_freezes_to_credit,
                transaction_type=TransactionTypeEnum.CREDIT.value,
                activity_id=StreakFreezeActivityNameEnum.STREAK_UNFREEZE.value,
                entity_id=None,
                entity_type=None,
            ),
        ]
        adapter.resources.update_user_resources(update_user_resource_dtos)

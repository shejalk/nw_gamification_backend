from nw_activities.adapters.resources_service_adapter import \
    UpdateUserResourceDTO
from nw_activities.adapters.service_adapter import get_service_adapter
from nw_activities.exceptions.custom_exceptions import InvalidActivityException
from nw_activities.interactors.dtos import UserActivityDTO
from nw_activities.interactors.storage_interfaces.\
    activity_group_storage_interface import ActivityGroupStorageInterface
from nw_activities.interactors.storage_interfaces.\
    activity_storage_interface import ActivityStorageInterface


class CreateUserActivityInteractor:

    def __init__(self, activity_storage: ActivityStorageInterface,
                 activity_group_storage: ActivityGroupStorageInterface):
        self.activity_storage = activity_storage
        self.activity_group_storage = activity_group_storage

    def create_user_activity(self, user_activity_dto: UserActivityDTO):
        is_user_has_access_to_perform_activities = \
            self._is_user_has_access_to_perform_activities(
                user_activity_dto.user_id)
        if not is_user_has_access_to_perform_activities:
            return

        is_streak_enabled_user = self._is_streak_enabled(
            user_activity_dto.user_id)
        if is_streak_enabled_user:
            return

        self._validate_activity_details(user_activity_dto.activity_name_enum)

        self.activity_storage.create_user_activity_log(user_activity_dto)

        self._update_user_resources(user_activity_dto)

        self._update_user_activity_group_instance_leaderboards(
            user_activity_dto)

        is_activity_groups_enabled_for_user = \
            self._is_activity_group_enabled_for_user(user_activity_dto.user_id)

        if not is_activity_groups_enabled_for_user:
            return

        self._update_user_activity_group_association_completion_metrics(
            user_activity_dto)

    def create_user_streak_activity(self, user_activity_dto: UserActivityDTO):
        is_user_has_access_to_perform_activities = \
            self._is_streak_enabled(user_activity_dto.user_id)
        if not is_user_has_access_to_perform_activities:
            return

        self._validate_activity_details(user_activity_dto.activity_name_enum)

        self.activity_storage.create_user_activity_log(user_activity_dto)

        self._update_user_resources(user_activity_dto)

        self._update_user_activity_group_association_completion_metrics(
            user_activity_dto)

        self._update_user_activity_group_streak(user_activity_dto)

    def create_streak_activity_for_streak_enabled_user(
            self, user_activity_dto: UserActivityDTO):
        self._validate_activity_details(user_activity_dto.activity_name_enum)

        self.activity_storage.create_user_activity_log(user_activity_dto)

        self._update_user_resources(user_activity_dto)

        self._update_user_activity_group_association_completion_metrics(
            user_activity_dto)

        self._update_user_activity_group_streak(user_activity_dto)

    @staticmethod
    def _is_streak_enabled(user_id: str) -> bool:
        adapter = get_service_adapter()
        return adapter.gamification_wrapper.is_streak_enabled(user_id)

    def _validate_activity_details(self, activity_name_enum: str):
        is_valid_activity = self.activity_storage.is_valid_activity(
            activity_name_enum)
        if not is_valid_activity:
            raise InvalidActivityException

    def _update_user_activity_group_association_completion_metrics(
            self, user_activity_dto: UserActivityDTO):
        from nw_activities.interactors.\
            update_activity_group_association_completion_metrics.activity \
            import ActivityGroupAssociationActivityInteractor
        interactor = ActivityGroupAssociationActivityInteractor(
            self.activity_group_storage)
        interactor.update_associations_completion_metrics_of_type_activity(
            user_activity_dto)

    @staticmethod
    def _update_user_resources(user_activity_dto: UserActivityDTO):
        user_resource_dto = UpdateUserResourceDTO(
            user_id=user_activity_dto.user_id,
            activity_id=user_activity_dto.activity_name_enum,
            name_enum=user_activity_dto.resource_name_enum,
            value=user_activity_dto.resource_value,
            transaction_type=user_activity_dto.transaction_type,
            entity_id=user_activity_dto.entity_id,
            entity_type=user_activity_dto.entity_type,
        )
        adapter = get_service_adapter()
        adapter.resources.update_user_resources([user_resource_dto])

    @staticmethod
    def _update_user_activity_group_instance_leaderboards(
            user_activity_dto: UserActivityDTO):
        adapter = get_service_adapter()
        adapter.clubs.update_user_club_leaderboards(
            user_activity_dto.user_id,
            user_activity_dto.resource_value,
            user_activity_dto.resource_name_enum)

    @staticmethod
    def _is_user_has_access_to_perform_activities(user_id: str) -> bool:
        adapter = get_service_adapter()
        is_user_has_access_to_perform_activities = \
            adapter.gamification_wrapper\
            .is_user_has_access_to_perform_activities(user_id)
        return is_user_has_access_to_perform_activities

    @staticmethod
    def _is_activity_group_enabled_for_user(user_id: str) -> bool:
        adapter = get_service_adapter()
        user_activity_group_enabled_dtos = \
            adapter.gamification_wrapper.is_activity_groups_enabled_for_users([
                user_id])

        if user_activity_group_enabled_dtos:
            return user_activity_group_enabled_dtos[0].activity_group_enabled

        return False

    def _update_user_activity_group_streak(
            self, user_activity_dto: UserActivityDTO):
        from nw_activities.interactors.update_user_activity_group_streak \
            import UpdateUserActivityGroupStreakInteractor
        interactor = UpdateUserActivityGroupStreakInteractor(
            self.activity_group_storage)
        interactor.update_user_activity_group_streak_based_on_activity(
            user_activity_dto)

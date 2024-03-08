import uuid

import factory

from nw_activities.adapters.gamification_wrapper_service.gamification_wrapper\
    import UserActivityGroupEnabledDTO
from nw_activities.adapters.resources_service_adapter import \
    UpdateUserResourceDTO, UserResourceDTO
from nw_activities.constants.enum import TransactionTypeEnum, ResourceNameEnum


class UpdateUserResourceDTOFactory(factory.Factory):
    class Meta:
        model = UpdateUserResourceDTO

    @factory.lazy_attribute
    def user_id(self):
        return str(uuid.uuid4())

    name_enum = factory.Sequence(
        lambda n: f"resource_name_enum_{n + 1}")
    value = factory.Sequence(lambda n: n + 1)
    transaction_type = factory.Iterator(
        TransactionTypeEnum.get_list_of_values())
    activity_id = factory.Sequence(lambda n: f"activity_id_{n + 1}")
    entity_id = factory.Sequence(lambda n: f"entity_id_{n + 1}")
    entity_type = factory.Sequence(lambda n: f"entity_type_{n + 1}")


class UserActivityGroupEnabledDTOFactory(factory.Factory):
    class Meta:
        model = UserActivityGroupEnabledDTO

    @factory.lazy_attribute
    def user_id(self):
        return str(uuid.uuid4())

    activity_group_enabled = False


class UserResourceDTOFactory(factory.Factory):
    class Meta:
        model = UserResourceDTO

    @factory.lazy_attribute
    def user_resource_id(self):
        return str(uuid.uuid4())

    final_value = factory.Sequence(lambda n: n + 1)

    @factory.lazy_attribute
    def user_id(self):
        return str(uuid.uuid4())

    resource_name_enum = factory.Iterator(
        ResourceNameEnum.get_list_of_values())

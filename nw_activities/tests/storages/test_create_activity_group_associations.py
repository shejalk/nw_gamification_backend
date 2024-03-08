import pytest

from nw_activities.models import ActivityGroupAssociation
from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import ActivityGroupFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupAssociationDTOFactory


@pytest.mark.django_db
class TestCreateActivityGroupAssociations:
    def test_creates_activity_group_associations(self):
        activity_groups = ActivityGroupFactory.create_batch(size=2)
        activity_group_association_dtos = [
            ActivityGroupAssociationDTOFactory(
                activity_group_id=str(activity_group.id))
            for activity_group in activity_groups
        ]
        storage = ActivityGroupStorageImplementation()

        storage.create_activity_group_associations(
            activity_group_association_dtos)

        activity_group_association_wise_obj = {
            str(obj.id): obj
            for obj in ActivityGroupAssociation.objects.all()
        }
        for dto in activity_group_association_dtos:
            obj = activity_group_association_wise_obj[dto.id]
            assert dto.activity_group_id == str(obj.activity_group_id)
            assert dto.association_id == obj.association_id
            assert dto.association_type == obj.association_type

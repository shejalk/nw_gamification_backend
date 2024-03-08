import uuid

import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import \
    ActivityGroupAssociationFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupAssociationDTOFactory


@pytest.mark.django_db
class TestGetActivityGroupAssociationsForAssociationIds:
    @pytest.fixture
    def setup_data(self):
        activity_group_associations = [
            ActivityGroupAssociationFactory(),
            ActivityGroupAssociationFactory(),
        ]
        ActivityGroupAssociationFactory()
        association_ids = [
            obj.association_id for obj in activity_group_associations
        ]

        expected_response = [
            ActivityGroupAssociationDTOFactory(
                id=str(activity_group_association.id),
                activity_group_id=str(
                    activity_group_association.activity_group_id),
                association_id=activity_group_association.association_id,
            )
            for activity_group_association in activity_group_associations
        ]

        association_ids += [str(uuid.uuid4())]
        return association_ids, expected_response

    def test_returns_activity_group_association_dtos(self, setup_data):
        association_ids, expected_response = setup_data
        storage = ActivityGroupStorageImplementation()

        response = storage.get_activity_group_associations_for_association_ids(
            association_ids)

        assert len(expected_response) == len(response)
        for dto in response:
            assert dto in expected_response

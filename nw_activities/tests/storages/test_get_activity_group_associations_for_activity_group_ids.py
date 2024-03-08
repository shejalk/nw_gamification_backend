import uuid

import pytest

from nw_activities.storages.activity_group_storage_implementation import \
    ActivityGroupStorageImplementation
from nw_activities.tests.factories.models import \
    ActivityGroupAssociationFactory
from nw_activities.tests.factories.storage_dtos import \
    ActivityGroupAssociationDTOFactory


@pytest.mark.django_db
class TestGetActivityGroupAssociationsForActivityGroupIds:
    @pytest.fixture
    def setup_data(self):
        activity_group_associations = [
            ActivityGroupAssociationFactory(),
            ActivityGroupAssociationFactory(),
        ]
        ActivityGroupAssociationFactory()
        activity_group_ids = [
            obj.activity_group_id for obj in activity_group_associations
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

        activity_group_ids += [str(uuid.uuid4())]
        return activity_group_ids, expected_response

    def test_returns_activity_group_association_dtos(self, setup_data):
        activity_group_ids, expected_response = setup_data
        storage = ActivityGroupStorageImplementation()

        response = storage.\
            get_activity_group_associations_for_activity_group_ids(
                activity_group_ids)

        assert len(expected_response) == len(response)
        for dto in response:
            assert dto in expected_response

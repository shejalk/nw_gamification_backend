from typing import List, Dict

from nw_activities.utils.spread_sheet_util import GSpreadPopulateUtils


class GetActivityGroupAssociationDataFromSpreadSheetUtil(GSpreadPopulateUtils):

    def load_activity_group_association_data_from_spread_sheet(
            self, spread_sheet_name: str, sub_sheet_name: str):
        activity_group_associations = self.format_spread_sheet_data(
            spread_sheet_name, sub_sheet_name)

        from nw_activities.interactors.data_loading\
            .create_activity_group_associations \
            import CreateActivityGroupAssociationInteractor
        from nw_activities.storages.activity_group_storage_implementation \
            import ActivityGroupStorageImplementation
        from nw_activities.storages.activity_storage_implementation import \
            ActivityStorageImplementation

        activity_storage = ActivityStorageImplementation()
        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = CreateActivityGroupAssociationInteractor(
            activity_group_storage, activity_storage)

        interactor.create_activity_group_associations(
            activity_group_associations)

    def format_spread_sheet_data(
            self, spread_sheet_name: str, sub_sheet_name: str) -> \
            List[Dict[str, str]]:
        sheet_data = self.get_sheet_data_using_spread_sheet_name(
            spread_sheet_name, sub_sheet_name)[1:]

        no_of_rows = len(sheet_data)
        index = 0

        activity_group_associations = []
        while index < no_of_rows:
            row = sheet_data[index]
            activity_group_association = {
                "id": row[0],
                "activity_group_id": row[1],
                "association_id": row[2],
                "association_type": row[3],
            }
            activity_group_associations.append(activity_group_association)
            index += 1

        return activity_group_associations

from typing import List, Dict

from nw_activities.utils.spread_sheet_util import GSpreadPopulateUtils


class GetActivityDataFromSpreadSheetUtil(GSpreadPopulateUtils):

    def load_activity_data_from_spread_sheet(
            self, spread_sheet_name: str, sub_sheet_name: str):
        activities = self.format_spread_sheet_data(
            spread_sheet_name, sub_sheet_name)

        from nw_activities.interactors.data_loading.create_activities import \
            CreateActivityInteractor
        from nw_activities.storages.activity_storage_implementation import \
            ActivityStorageImplementation
        activity_storage = ActivityStorageImplementation()
        interactor = CreateActivityInteractor(activity_storage)

        interactor.create_activities(activities)

    def format_spread_sheet_data(
            self, spread_sheet_name: str, sub_sheet_name: str) -> \
            List[Dict[str, str]]:
        sheet_data = self.get_sheet_data_using_spread_sheet_name(
            spread_sheet_name, sub_sheet_name)[1:]

        no_of_rows = len(sheet_data)
        index = 0

        activities = []
        while index < no_of_rows:
            row = sheet_data[index]
            activity = {
                "name_enum": row[0],
                "name": row[1],
                "description": row[2],
            }
            activities.append(activity)
            index += 1

        return activities

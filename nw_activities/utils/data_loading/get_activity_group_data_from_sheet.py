import json
from typing import List, Dict

from nw_activities.utils.spread_sheet_util import GSpreadPopulateUtils


class GetActivityGroupDataFromSpreadSheetUtil(GSpreadPopulateUtils):

    def load_activity_group_data_from_spread_sheet(
            self, spread_sheet_name: str, sub_sheet_name: str):
        activity_groups = self.format_spread_sheet_data(
            spread_sheet_name, sub_sheet_name)

        from nw_activities.interactors.data_loading.create_activity_groups \
            import CreateActivityGroupInteractor
        from nw_activities.storages.activity_group_storage_implementation \
            import ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = CreateActivityGroupInteractor(activity_group_storage)

        interactor.create_activity_groups(activity_groups)

    def format_spread_sheet_data(
            self, spread_sheet_name: str, sub_sheet_name: str) -> \
            List[Dict[str, str]]:
        sheet_data = self.get_sheet_data_using_spread_sheet_name(
            spread_sheet_name, sub_sheet_name)[1:]

        no_of_rows = len(sheet_data)
        index = 0

        activity_groups = []
        while index < no_of_rows:
            row = sheet_data[index]
            activity = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "frequency_type": row[3],
                "frequency_config": json.loads(row[4]),
                "reward_config_ids":
                    self._convert_strings_with_newlines_to_list(row[5]),
            }
            activity_groups.append(activity)
            index += 1

        return activity_groups

    @staticmethod
    def _convert_strings_with_newlines_to_list(strings: str) -> List[str]:
        strings_list = strings.split("\n")
        return [each.strip() for each in strings_list if each]

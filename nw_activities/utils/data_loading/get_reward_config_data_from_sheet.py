from typing import List, Dict

from nw_activities.utils.spread_sheet_util import GSpreadPopulateUtils


class GetRewardConfigsDataFromSpreadSheetUtil(GSpreadPopulateUtils):

    def load_reward_configs_data_from_spread_sheet(
            self, spread_sheet_name: str, sub_sheet_name: str):
        completion_metrics = self.format_spread_sheet_data(
            spread_sheet_name, sub_sheet_name)

        from nw_activities.interactors.data_loading.create_reward_configs \
            import CreateRewardConfigInteractor
        from nw_activities.storages.activity_group_storage_implementation \
            import ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = CreateRewardConfigInteractor(activity_group_storage)

        interactor.create_reward_configs(completion_metrics)

    def format_spread_sheet_data(
            self, spread_sheet_name: str, sub_sheet_name: str) -> \
            List[Dict[str, str]]:
        sheet_data = self.get_sheet_data_using_spread_sheet_name(
            spread_sheet_name, sub_sheet_name)[1:]

        no_of_rows = len(sheet_data)
        index = 0

        reward_configs = []
        while index < no_of_rows:
            row = sheet_data[index]
            activity = {
                "id": row[0],
                "resource_reward_config_id": row[1],
            }
            reward_configs.append(activity)
            index += 1

        return reward_configs

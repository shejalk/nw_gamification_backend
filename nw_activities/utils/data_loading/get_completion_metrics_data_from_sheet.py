from typing import List, Dict, Any, Optional

from nw_activities.utils.spread_sheet_util import GSpreadPopulateUtils


class GetCompletionMetricsDataFromSpreadSheetUtil(GSpreadPopulateUtils):

    def load_completion_metrics_data_from_spread_sheet(
            self, spread_sheet_name: str, sub_sheet_name: str):
        completion_metrics = self.format_spread_sheet_data(
            spread_sheet_name, sub_sheet_name)

        from nw_activities.interactors.data_loading.create_completion_metrics \
            import CreateCompletionMetricInteractor
        from nw_activities.storages.activity_group_storage_implementation \
            import ActivityGroupStorageImplementation

        activity_group_storage = ActivityGroupStorageImplementation()
        interactor = CreateCompletionMetricInteractor(activity_group_storage)

        interactor.create_completion_metrics(completion_metrics)

    def format_spread_sheet_data(
            self, spread_sheet_name: str, sub_sheet_name: str) -> \
            List[Dict[str, Any]]:
        sheet_data = self.get_sheet_data_using_spread_sheet_name(
            spread_sheet_name, sub_sheet_name)[1:]

        no_of_rows = len(sheet_data)
        index = 0

        completion_metrics = []
        while index < no_of_rows:
            row = sheet_data[index]
            activity = {
                "id": row[0],
                "entity_id": row[1],
                "entity_type": row[2],
                "value": self._convert_string_to_float(row[3]),
                "activity_group_ids":
                    self._convert_strings_with_newlines_to_list(row[4]),
            }
            completion_metrics.append(activity)
            index += 1

        return completion_metrics

    @staticmethod
    def _convert_string_to_float(value: str) -> Optional[float]:
        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _convert_strings_with_newlines_to_list(strings: str) -> List[str]:
        strings_list = strings.split("\n")
        return [each.strip() for each in strings_list if each]

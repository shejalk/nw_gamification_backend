import json
from collections import Counter, defaultdict
from typing import Dict, Any, List

from ib_common.date_time_utils.convert_string_to_local_date_time import \
    convert_string_to_local_date_time
from nw_activities.constants.constants import TIME_FORMAT
from nw_activities.constants.enum import FrequencyTypeEnum, \
    FrequencyPeriodEnum, WeekDayEnum
from nw_activities.exceptions.custom_exceptions import \
    InvalidInputDataException
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import ActivityGroupStorageInterface, \
    CreateActivityGroupDTO


class CreateActivityGroupInteractor:

    def __init__(self, activity_group_storage: ActivityGroupStorageInterface):
        self.activity_group_storage = activity_group_storage

    def create_activity_groups(self, activity_groups: List[Dict[str, Any]]):
        """
        :param activity_groups: [{
            "id": string
            "name": string
            "description": optional[string]
            "frequency_type": string
            "frequency_config": Dict
            "completion_metric_ids": List[str]
            "reward_config_ids": List[str]
        }]
        :type activity_groups: List[Dict[str, Any]]
        :return:
        :rtype:
        """
        self._validate_activity_groups(activity_groups)

        create_activity_group_dtos = [
            CreateActivityGroupDTO(
                id=each['id'],
                name=each['name'],
                description=each['description'],
                frequency_type=each['frequency_type'],
                frequency_config=json.dumps(each['frequency_config']),
                reward_config_ids=each['reward_config_ids'],
            )
            for each in activity_groups
        ]

        self.activity_group_storage.create_activity_groups(
            create_activity_group_dtos)

    def _validate_activity_groups(self, activity_groups: List[Dict[str, Any]]):
        activity_group_ids = [each['id'] for each in activity_groups]
        invalid_activity_group_ids = self._get_invalid_activity_group_ids(
            activity_group_ids)

        invalid_frequency_types = self._get_invalid_frequency_types(
            activity_groups)

        activity_group_id_wise_invalid_frequency_config_data = \
            self._get_activity_group_id_wise_invalid_frequency_config_data(
                activity_groups)

        activity_group_id_wise_invalid_reward_config_ids = \
            self._get_activity_group_id_wise_invalid_reward_config_ids(
                activity_groups)

        invalid_reward_config_ids = self._get_invalid_reward_config_ids(
            activity_groups)

        invalid_data = {}
        if invalid_frequency_types:
            invalid_data['invalid_frequency_types'] = invalid_frequency_types

        if invalid_activity_group_ids:
            invalid_data['invalid_activity_group_ids'] = \
                invalid_activity_group_ids

        if activity_group_id_wise_invalid_frequency_config_data:
            invalid_data[
                'activity_group_id_wise_invalid_frequency_config_data'] = \
                activity_group_id_wise_invalid_frequency_config_data

        if activity_group_id_wise_invalid_reward_config_ids:
            invalid_data['activity_group_id_wise_invalid_reward_config_ids'] \
                = activity_group_id_wise_invalid_reward_config_ids

        if invalid_reward_config_ids:
            invalid_data['invalid_reward_config_ids'] = \
                invalid_reward_config_ids

        if invalid_data:
            raise InvalidInputDataException(invalid_data)

    def _get_activity_group_id_wise_invalid_reward_config_ids(
            self, activity_groups: List[Dict[str, Any]]) -> \
            Dict[str, List[str]]:
        activity_group_id_wise_reward_config_ids = {
            each['id']: each['reward_config_ids']
            for each in activity_groups
        }

        activity_group_ids = list(
            activity_group_id_wise_reward_config_ids.keys())
        existing_activity_groups_reward_config_dtos = \
            self.activity_group_storage.get_activity_group_reward_configs(
                activity_group_ids)

        existing_activity_group_id_wise_reward_config_ids = \
            defaultdict(list)
        for dto in existing_activity_groups_reward_config_dtos:
            existing_activity_group_id_wise_reward_config_ids[
                dto.activity_group_id].append(dto.id)

        activity_group_id_wise_invalid_reward_config_ids = {}
        for activity_group_id, reward_config_ids in \
                activity_group_id_wise_reward_config_ids.items():
            existing_reward_config_ids = \
                existing_activity_group_id_wise_reward_config_ids[
                    activity_group_id]
            invalid_reward_config_ids = list(
                set(reward_config_ids) & set(existing_reward_config_ids),
            )
            if invalid_reward_config_ids:
                activity_group_id_wise_invalid_reward_config_ids[
                    activity_group_id] = invalid_reward_config_ids

        return activity_group_id_wise_invalid_reward_config_ids

    @staticmethod
    def _get_invalid_frequency_types(activity_groups: List[Dict[str, Any]]) -> \
            List[str]:
        frequency_types = [
            each['frequency_type']
            for each in activity_groups
        ]
        existing_frequency_types = FrequencyTypeEnum.get_list_of_values()
        invalid_frequency_types = list(
            set(frequency_types) - set(existing_frequency_types),
        )
        return invalid_frequency_types

    def _get_invalid_activity_group_ids(self, activity_group_ids):
        existing_activity_group_ids = \
            self.activity_group_storage.get_existing_activity_group_ids(
                activity_group_ids)
        invalid_activity_group_ids = list(
            set(activity_group_ids) & set(existing_activity_group_ids),
        )
        return invalid_activity_group_ids

    def _get_activity_group_id_wise_invalid_frequency_config_data(
            self, activity_groups) -> Dict[str, Any]:
        activity_group_id_wise_invalid_frequency_config_data = {}
        for each in activity_groups:
            starts_at_list = each['frequency_config']['starts_at']
            ends_at_list = each['frequency_config']['ends_at']
            starts_at_value_types = [starts_at['value_type']
                                     for starts_at in starts_at_list]
            ends_at_value_types = [ends_at['value_type']
                                   for ends_at in ends_at_list]
            required_frequency_config_value_types = self\
                ._get_required_frequency_config_value_types(each) # pylint: disable=E1111

            if each['frequency_type'] == FrequencyTypeEnum.DAILY.value:
                required_frequency_config_value_types = [
                    FrequencyPeriodEnum.TIME.value,
                ]

            if each['frequency_type'] == FrequencyTypeEnum.WEEKLY.value:
                required_frequency_config_value_types = [
                    FrequencyPeriodEnum.TIME.value,
                    FrequencyPeriodEnum.DAY.value,
                ]

            duplicate_starts_at_value_types = \
                self._get_duplicates_in_the_list(starts_at_value_types)

            invalid_frequency_config_starts_at_value_types = \
                self._get_invalid_frequency_config_value_types(
                    starts_at_value_types)

            invalid_frequency_config_ends_at_value_types = \
                self._get_invalid_frequency_config_value_types(
                    ends_at_value_types)

            missing_frequency_config_value_types = \
                self._get_missing_frequency_config_value_types(
                    required_frequency_config_value_types,
                    starts_at_value_types)

            invalid_starts_at_data = \
                self._get_invalid_frequency_config_period_data(
                    starts_at_list)

            invalid_ends_at_data = \
                self._get_invalid_frequency_config_period_data(ends_at_list)

            invalid_data = {}
            if duplicate_starts_at_value_types:
                invalid_data["duplicate_starts_at_value_types"] = \
                    duplicate_starts_at_value_types
            if invalid_frequency_config_starts_at_value_types:
                invalid_data["invalid_frequency_config_starts_at_value_types"] \
                    = invalid_frequency_config_starts_at_value_types
            if invalid_frequency_config_ends_at_value_types:
                invalid_data["invalid_frequency_config_ends_at_value_types"] \
                    = invalid_frequency_config_ends_at_value_types
            if missing_frequency_config_value_types:
                invalid_data["missing_frequency_config_value_types"] = \
                    missing_frequency_config_value_types
            if invalid_starts_at_data:
                invalid_data["invalid_starts_at_data"] = invalid_starts_at_data
            if invalid_ends_at_data:
                invalid_data["invalid_ends_at_data"] = invalid_ends_at_data

            if invalid_data:
                activity_group_id_wise_invalid_frequency_config_data[
                    each['id']] = invalid_data

        return activity_group_id_wise_invalid_frequency_config_data

    @staticmethod
    def _get_duplicates_in_the_list(values: List[str]) -> List[str]:
        duplicate_values = [
            value for value, count in
            Counter(values).items() if count > 1
        ]
        return duplicate_values

    @staticmethod
    def _get_invalid_frequency_config_value_types(
            frequency_config_value_types: List[FrequencyPeriodEnum],
    ) -> List[FrequencyPeriodEnum]:
        return list(set(frequency_config_value_types) -
                    set(FrequencyPeriodEnum.get_list_of_values()))

    @staticmethod
    def _get_missing_frequency_config_value_types(
            required_frequency_periods: List[FrequencyPeriodEnum],
            frequency_periods: List[str]) -> List[FrequencyPeriodEnum]:
        missing_frequency_config_value_types = []
        for value_type in required_frequency_periods:
            if value_type not in frequency_periods:
                missing_frequency_config_value_types.append(value_type)
        return missing_frequency_config_value_types

    @staticmethod
    def _get_invalid_frequency_config_period_data(
            frequency_periods: List[Dict[str, str]]) -> List[Dict[str, str]]:
        invalid_frequency_period_data = []
        for each in frequency_periods:
            if each['value_type'] == FrequencyPeriodEnum.TIME.value:
                is_valid = convert_string_to_local_date_time(
                    each['value'], TIME_FORMAT)
                if not is_valid:
                    invalid_frequency_period_data.append(each)

            if each['value_type'] == FrequencyPeriodEnum.DAY.value:
                is_valid = each['value'] in WeekDayEnum.get_list_of_values()
                if not is_valid:
                    invalid_frequency_period_data.append(each)

        return invalid_frequency_period_data

    def _get_invalid_reward_config_ids(
            self, activity_groups: List[Dict[str, str]]) -> List[str]:
        reward_config_ids = []
        for each in activity_groups:
            reward_config_ids.extend(each['reward_config_ids'])

        existing_reward_config_ids = \
            self.activity_group_storage.get_existing_reward_config_ids(
                reward_config_ids)

        invalid_reward_config_ids = list(
            set(reward_config_ids) - set(existing_reward_config_ids),
        )

        return invalid_reward_config_ids

    def _get_required_frequency_config_value_types(
            self, activity_group: Dict[str, Any]) -> List[str]:
        pass

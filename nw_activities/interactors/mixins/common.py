import datetime
from typing import Dict, List, Any, Tuple, Optional

from ib_common.date_time_utils.get_current_local_date_time import \
    get_current_local_date_time

from nw_activities.constants.config import WEEK_DAY_WISE_INDEX
from nw_activities.constants.constants import DATE_FORMAT, \
    DATETIME_INSTANCE_IDENTIFIER_FORMAT, DATE_TIME_FORMAT, \
    INSTANCE_IDENTIFIER_SEPARATOR
from nw_activities.constants.enum import FrequencyTypeEnum, FrequencyPeriodEnum
from nw_activities.interactors.storage_interfaces. \
    activity_group_storage_interface import \
    ActivityGroupFrequencyConfigDTO, ActivityGroupInstanceIdentifierDTO


class CommonMixin:

    def get_activity_group_instance_identifier(
            self, activity_group_frequency_config_dtos:
            List[ActivityGroupFrequencyConfigDTO], _date: datetime.date = None,
    ) -> List[ActivityGroupInstanceIdentifierDTO]:
        activity_group_instance_identifier_dtos = []
        for dto in activity_group_frequency_config_dtos:
            instance_identifier = None
            if dto.frequency_type == FrequencyTypeEnum.DAILY.value:
                instance_identifier = \
                    self._get_daily_activity_group_instance_identifier(
                        dto.config, _date)

            if dto.frequency_type == FrequencyTypeEnum.WEEKLY.value:
                instance_identifier = \
                    self._get_weekly_activity_group_instance_identifier(
                        dto.config, _date)

            activity_group_instance_identifier_dtos.append(
                ActivityGroupInstanceIdentifierDTO(
                    activity_group_id=dto.activity_group_id,
                    instance_identifier=instance_identifier,
                ),
            )

        return activity_group_instance_identifier_dtos

    @staticmethod
    def _get_daily_activity_group_instance_identifier(
            activity_group_frequency_config: Dict[str, List[Any]],
            _date: Optional[datetime.date] = None,
    ) -> str:
        starts_at = activity_group_frequency_config["starts_at"][0]
        ends_at = activity_group_frequency_config["ends_at"][0]

        date_to_consider = _date
        if not _date:
            date_to_consider = get_current_local_date_time().date()

        start_date_str = datetime.date.strftime(date_to_consider, DATE_FORMAT)
        end_date_str = datetime.date.strftime(date_to_consider, DATE_FORMAT)

        start_datetime_str = start_date_str + " " + starts_at['value']
        end_datetime_str = end_date_str + " " + ends_at["value"]

        instance_identifier = DATETIME_INSTANCE_IDENTIFIER_FORMAT.format(
            start_datetime_str=start_datetime_str,
            end_datetime_str=end_datetime_str)

        return instance_identifier

    def _get_weekly_activity_group_instance_identifier(
            self, activity_group_frequency_config: Dict[str, List[Any]],
            _date: datetime.date = None,
    ) -> str:
        starts_at = activity_group_frequency_config["starts_at"]
        ends_at = activity_group_frequency_config["ends_at"]

        date_to_consider = _date
        if not _date:
            date_to_consider = get_current_local_date_time().date()

        start_week_day, start_time_str = None, None
        for each in starts_at:
            if each['value_type'] == FrequencyPeriodEnum.TIME.value:
                start_time_str = each['value']
            if each['value_type'] == FrequencyPeriodEnum.DAY.value:
                start_week_day = each['value']

        end_week_day, end_time_str = None, None
        for each in ends_at:
            if each['value_type'] == FrequencyPeriodEnum.TIME.value:
                end_time_str = each['value']
            if each['value_type'] == FrequencyPeriodEnum.DAY.value:
                end_week_day = each['value']

        start_week_day_index = WEEK_DAY_WISE_INDEX[start_week_day]
        end_week_day_index = WEEK_DAY_WISE_INDEX[end_week_day]

        start_date = self.get_given_week_date(
            date_to_consider, start_week_day_index)
        end_date = self.get_given_week_date(
            date_to_consider, end_week_day_index)

        start_date_str = datetime.date.strftime(start_date, DATE_FORMAT)
        end_date_str = datetime.date.strftime(end_date, DATE_FORMAT)

        start_datetime_str = start_date_str + " " + start_time_str
        end_datetime_str = end_date_str + " " + end_time_str

        instance_identifier = DATETIME_INSTANCE_IDENTIFIER_FORMAT.format(
            start_datetime_str=start_datetime_str,
            end_datetime_str=end_datetime_str)

        return instance_identifier

    @staticmethod
    def get_given_week_date(input_date: datetime.date, week_day_index: int) \
            -> datetime.date:
        from nw_activities.constants.constants import MIN_WEEK_DAY
        days_diff = input_date.weekday() - MIN_WEEK_DAY
        week_date = input_date - datetime.timedelta(days=days_diff)

        while True:
            if week_date.weekday() == week_day_index:
                return week_date
            week_date = week_date + datetime.timedelta(days=1)

    @staticmethod
    def format_instance_identifier(
            start_datetime: datetime.datetime,
            end_datetime: datetime.datetime) -> str:
        start_datetime_str = datetime.date.strftime(
            start_datetime, DATE_TIME_FORMAT)
        end_datetime_str = datetime.date.strftime(
            end_datetime, DATE_TIME_FORMAT)
        instance_identifier = DATETIME_INSTANCE_IDENTIFIER_FORMAT.format(
            start_datetime_str=start_datetime_str,
            end_datetime_str=end_datetime_str)
        return instance_identifier

    @staticmethod
    def split_instance_identifier_into_datetime_objects(
            instance_identifier: str,
    ) -> Tuple[datetime.datetime, datetime.datetime]:
        start_date_identifier, end_date_identifier = \
            instance_identifier.split(INSTANCE_IDENTIFIER_SEPARATOR)
        start_datetime = datetime.datetime.strptime(
            start_date_identifier, DATE_TIME_FORMAT)
        end_datetime = datetime.datetime.strptime(
            end_date_identifier, DATE_TIME_FORMAT)
        return start_datetime, end_datetime

    def get_activity_group_instance_identifiers_between_dates(
            self, activity_group_frequency_config_dtos:
            List[ActivityGroupFrequencyConfigDTO],
            from_date: datetime.date, to_date: datetime.date,
    ) -> List[ActivityGroupInstanceIdentifierDTO]:
        date_ranges = [
            from_date + datetime.timedelta(days=day_count)
            for day_count in range((to_date - from_date).days + 1)
        ]
        activity_group_instance_identifier_dtos = []
        for dto in activity_group_frequency_config_dtos:
            instance_identifiers = []
            for _date in date_ranges:
                instance_identifier = None
                if dto.frequency_type == FrequencyTypeEnum.DAILY.value:
                    instance_identifier = \
                        self._get_daily_activity_group_instance_identifier(
                            dto.config, _date)

                if dto.frequency_type == FrequencyTypeEnum.WEEKLY.value:
                    instance_identifier = \
                        self._get_weekly_activity_group_instance_identifier(
                            dto.config, _date)

                if instance_identifier in instance_identifiers:
                    continue

                activity_group_instance_identifier_dtos.append(
                    ActivityGroupInstanceIdentifierDTO(
                        activity_group_id=dto.activity_group_id,
                        instance_identifier=instance_identifier,
                    ),
                )

        return activity_group_instance_identifier_dtos

    def get_activity_group_instance_identifiers_for_date(
            self, activity_group_frequency_config_dtos:
            List[ActivityGroupFrequencyConfigDTO],
            input_date: datetime.date,
    ) -> List[ActivityGroupInstanceIdentifierDTO]:
        activity_group_instance_identifier_dtos = []
        instance_identifiers = []
        for dto in activity_group_frequency_config_dtos:
            instance_identifier = None
            if dto.frequency_type == FrequencyTypeEnum.DAILY.value:
                instance_identifier = \
                    self._get_daily_activity_group_instance_identifier(
                        dto.config, input_date)

            if dto.frequency_type == FrequencyTypeEnum.WEEKLY.value:
                instance_identifier = \
                    self._get_weekly_activity_group_instance_identifier(
                        dto.config, input_date)

            if not instance_identifier:
                continue

            if instance_identifier in instance_identifiers:
                continue

            activity_group_instance_identifier_dtos.append(
                ActivityGroupInstanceIdentifierDTO(
                    activity_group_id=dto.activity_group_id,
                    instance_identifier=instance_identifier,
                ),
            )

        return activity_group_instance_identifier_dtos

    def get_activity_group_instance_identifier_for_given_dates(
            self, activity_group_frequency_config_dtos:
            List[ActivityGroupFrequencyConfigDTO],
            input_dates: List[datetime.date]) \
            -> List[ActivityGroupInstanceIdentifierDTO]:

        activity_group_instance_identifier_dtos = []

        for each_date in input_dates:
            activity_group_instance_identifier_dtos.extend(
                self.get_activity_group_instance_identifiers_for_date(
                    activity_group_frequency_config_dtos, each_date,
                ),
            )

        return activity_group_instance_identifier_dtos

TIME_FORMAT = "%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
DATE_TIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT
INSTANCE_IDENTIFIER_SEPARATOR = "#"

DATETIME_INSTANCE_IDENTIFIER_FORMAT = \
    "{start_datetime_str}" + \
    INSTANCE_IDENTIFIER_SEPARATOR + "{end_datetime_str}"

# Day 0 is monday in a week
MIN_WEEK_DAY = 0

STREAK_STARTED_EVENT_VALUE = 1

ACTIVITY_ID_FOR_MANUAL_UPDATION = "UPDATE_CONSISTENCY_SCORE_MANUALLY"

MAXIMUM_FREEZES_ALLOWED_PER_MONTH = 3
from nw_activities.constants.enum import WeekDayEnum

WEEK_DAY_WISE_INDEX = {
    WeekDayEnum.MONDAY.value: 0,
    WeekDayEnum.TUESDAY.value: 1,
    WeekDayEnum.WEDNESDAY.value: 2,
    WeekDayEnum.THURSDAY.value: 3,
    WeekDayEnum.FRIDAY.value: 4,
    WeekDayEnum.SATURDAY.value: 5,
    WeekDayEnum.SUNDAY.value: 6,
}

CONSISTENCY_SCORE_DEDUCTION_MULTIPLIER_CONFIG = [
    {
        "min_score": 1,
        "max_score": 499,
        "deduction_multiplier": 1,
    },
    {
        "min_score": 500,
        "max_score": 4999,
        "deduction_multiplier": 5,
    },
    {
        "min_score": 5000,
        "max_score": 9999,
        "deduction_multiplier": 25,
    },
    {
        "min_score": 10000,
        "max_score": None,
        "deduction_multiplier": 100,
    },
]

MAXIMUM_FREEZES_ALLOWED_PER_MONTH = 3

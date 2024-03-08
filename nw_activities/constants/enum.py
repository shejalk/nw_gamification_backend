import enum
from ib_common.constants import BaseEnumClass


class TransactionTypeEnum(BaseEnumClass, enum.Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class FrequencyTypeEnum(BaseEnumClass, enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"


class FrequencyPeriodEnum(BaseEnumClass, enum.Enum):
    TIME = "TIME"
    DAY = "DAY"


class WeekDayEnum(BaseEnumClass, enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class OperatorEnum(BaseEnumClass, enum.Enum):
    EQ = "EQ"
    LT = "LT"
    GT = "GT"
    GTE = "GTE"
    LTE = "LTE"
    BETWEEN = "BETWEEN"
    STEP = "STEP"


class CompletionStatusEnum(BaseEnumClass, enum.Enum):
    COMPLETED = "COMPLETED"
    IN_PROGRESS = "IN_PROGRESS"
    YET_TO_START = "YET_TO_START"


class ActivityGroupAssociationTypeEnum(BaseEnumClass, enum.Enum):
    ACTIVITY = "ACTIVITY"
    ACTIVITY_GROUP = "ACTIVITY_GROUP"


class CompletionMetricEntityTypeEnum(BaseEnumClass, enum.Enum):
    RESOURCE = "RESOURCE"
    ACTIVITY_GROUP_ASSOCIATION = "ACTIVITY_GROUP_ASSOCIATION"


class RewardTypeEnum(BaseEnumClass, enum.Enum):
    RESOURCE_BASED = "RESOURCE_BASED"
    COMPLETION_BASED = "COMPLETION_BASED"


class RewardEntityTypeEnum(BaseEnumClass, enum.Enum):
    ACTIVITY = "ACTIVITY"
    USER_ACTIVITY_GROUP_INSTANCE = "USER_ACTIVITY_GROUP_INSTANCE"


class WebSocketActionEnum(BaseEnumClass, enum.Enum):
    ACTIVITY_GROUP_COMPLETED = "ACTIVITY_GROUP_COMPLETED"
    ACTIVITY_GROUP_STREAK_STARTED = "ACTIVITY_GROUP_STREAK_STARTED"
    ACTIVITY_GROUP_STREAK_UPDATED = "ACTIVITY_GROUP_STREAK_UPDATED"
    USER_CONSISTENCY_SCORE_CREDITED = "USER_CONSISTENCY_SCORE_CREDITED"


class InstanceTypeEnum(BaseEnumClass, enum.Enum):
    DEFAULT = "DEFAULT"
    LEISURE = "LEISURE"
    PAUSED = "PAUSED"
    NO_ACTIVITY = "NO_ACTIVITY"
    FREEZE = "FREEZE"


class OptionalMetricEntityTypeEnum(BaseEnumClass, enum.Enum):
    RESOURCE = "RESOURCE"


class ResourceNameEnum(BaseEnumClass, enum.Enum):
    POINTS = "POINTS"
    COINS = "COINS"
    CONSISTENCY_SCORE = "CONSISTENCY_SCORE"
    STREAK_FREEZES = "STREAK_FREEZES"


class ResourceEntityTypeEnum(BaseEnumClass, enum.Enum):
    ACTIVITY_GROUP = "ACTIVITY_GROUP"
    USER_ACTIVITY_GROUP_INSTANCE = "USER_ACTIVITY_GROUP_INSTANCE"


class StreakFreezeActivityNameEnum(BaseEnumClass, enum.Enum):
    STREAK_FREEZE = "STREAK_FREEZE"
    STREAK_UNFREEZE = "STREAK_UNFREEZE"


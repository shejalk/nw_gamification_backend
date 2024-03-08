

REQUEST_BODY_JSON = """
{
    "freeze_date": "2099-12-31"
}
"""


RESPONSE_200_JSON = """
{
    "response": "string",
    "http_status_code": 1,
    "res_status": "STREAK_FREEZED_SUCCESSFULLY"
}
"""

RESPONSE_400_JSON = """
{
    "response": "string",
    "http_status_code": 1,
    "res_status": "MONTHLY_FREEZE_LIMIT_EXCEEDED"
}
"""


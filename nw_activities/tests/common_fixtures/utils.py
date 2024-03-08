from nw_activities.tests.common_fixtures import get_mock_object


def generate_uuid_mock(mocker):
    from nw_activities.utils import generate_uuid
    func_to_mock = generate_uuid.generate_uuid
    mock = get_mock_object(mocker, func_to_mock)
    return mock

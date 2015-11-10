import pytest

def pytest_addoption(parser):
    parser.addoption('--server',
        action="store",
        default='http://localhost:9000',
        help='Base URL for server to test.')

@pytest.fixture
def server(request):
    return request.config.getoption('--server')
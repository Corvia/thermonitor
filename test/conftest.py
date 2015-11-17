import pytest

# Initialize Django
# http://stackoverflow.com/a/11158224
import inspect, os, sys
cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(cwd)
sys.path.insert(0, parentdir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djthermonitor.settings")
from django.core.management import execute_from_command_line
execute_from_command_line([''])
# End Django initialization

def pytest_addoption(parser):
    parser.addoption('--server',
        action="store",
        default='http://localhost:9000',
        help='Base URL for server to test.')

@pytest.fixture
def server(request):
    return request.config.getoption('--server')
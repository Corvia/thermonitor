from djthermonitor.settings import DEBUG


def settings(request):
    return {
        'settings': {
            'DEBUG': DEBUG
        }
    }

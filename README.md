# thermonitor

A hardware + web application project to continuously monitor thermometers and to
dispatch notification if they dip above or below regular operating temperatures.

![](http://bpk-disk.s3.amazonaws.com/v1MVP.png)

## Documentation
### API
The Thermonitor REST API specification can be found at `docs/api.yaml`. An HTML
version of this document can be viewed using the
[Swagger editor](http://editor.swagger.io/).

## Tests
Tests are located in the `test` directory and can be run with `pytest`, e.g.,

    $ py.test -v

The REST API tests depend on a running web server. The simplest way to achieve
 thisis to use Django's built-in web server, e.g.,

    $ cd thermonitor
    $ source bin/activate
    $ python manage.py runserver 0.0.0.0:9000

An optional `--server` command line argument dictates the base URL the tests
use, e.g.,

    $ py.test -v --server=http://127.0.0.1:9000
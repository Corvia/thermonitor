# thermonitor

A hardware + web application project to continuously monitor thermometers and to
dispatch notification if they dip above or below regular operating temperatures.

![](http://bpk-disk.s3.amazonaws.com/v1MVP.png)

## Documentation
### API
The Thermonitor REST API specification can be found at `docs/api.yaml`. An HTML
version of this document can be viewed using the
[Swagger editor](http://editor.swagger.io/).

## Development
### Front End
The front end is built using [React](https://facebook.github.io/react/) and
transformed ahead of time using
[`browserify`](https://github.com/substack/node-browserify). When developing
(i.e., when `djthermonitor.settings.DEBUG == True`), the output is expected at
`static/js/bundle.js`. React, its dependencies, and the commands to build
`bundle.js` are specified in `package.json` and managed with `npm`. `npm` will
be installed automatically by `provision.sh` in VMs createed with `Vagrantfile`.
For other environments, please install node v5.0.0 or newer from
[https://nodejs.org/en/download/stable/](https://nodejs.org/en/download/stable/).

Once `npm` is available, simply run the following command from the project root
directory to build `bundle.js`:

    $ npm run start

This command will spawn a [`watchify`](https://github.com/substack/watchify)
process that will continuously monitor the `static/js` directory and build an
updated `bundle.js` as changes are made.

_NB: A known issue may prevent `watchify` from being notified of changes. See
[https://github.com/substack/watchify#rebuilds-on-os-x-never-trigger](https://github.com/substack/watchify#rebuilds-on-os-x-never-trigger)
for more information and potential fixes._

## Tests
Tests are located in the `test` directory and can be run with `pytest`, e.g.,

    $ py.test -v

## Build Process
### Front End
As mentioned above, the front end is built using React and transformed ahead of
time. For production (i.e., when `djthermonitor.settings.DEBUG == False`),
however, the output is also minified. The resulting file is expected at
`static/js/bundle.min.js`. Run the following command from the project root
directory to build `bundle.min.js`:

    $ npm run build
var AlertActions = require('../actions/AlertActions');
var AlertStore = require('../stores/AlertStore');
var Footer = require('./Footer.react');
var GraphSection = require('./GraphSection.react');
var Header = require('./Header.react');
var NotificationSection = require('./NotificationSection.react');
var React = require('react');
var SensorActions = require('../actions/SensorActions');
var SensorStore = require('../stores/SensorStore');
var ZoneActions = require('../actions/ZoneActions');
var ZoneSection = require('./ZoneSection.react');
var ZoneStore = require('../stores/ZoneStore');

var ThermonitorApp = React.createClass({
    componentDidMount: function() {
        AlertStore.addChangeListener(this._onChange);
        SensorStore.addChangeListener(this._onChange);
        ZoneStore.addChangeListener(this._onChange);

        this.requestData();
        var intervalId = setInterval(this.requestData, 10000);
        this.setState($.extend(this.state, {
            intervalId: intervalId
        }));
    },

    componentWillUnmount: function() {
        AlertStore.removeChangeListener(this._onChange);
        SensorStore.removeChangeListener(this._onChange);
        ZoneStore.removeChangeListener(this._onChange);
    },

    getInitialState: function() {
        return {};
    },

    render: function() {
        if (!this.state.hasOwnProperty('zones')) {
            return (
                <div>
                    <Header />
                    <div className="container loading"><h3>Loading…</h3></div>
                    <Footer />
                </div>
            );
        }

        return (
            <div>
                <Header />
                <GraphSection sensors={this.state.sensors} />
                <ZoneSection zones={this.state.zones} />
                <NotificationSection alerts={this.state.alerts} />
                <Footer />
            </div>
        );
    },

    requestData: function() {
        AlertActions.requestAlerts();
        ZoneActions.requestZones();
        SensorActions.requestSensors({
            zoneIds: Object.keys(this.state.zones)
        });
    },

    _onChange: function() {
        this.setState($.extend(this.state, {
            alerts: AlertStore.getAllAlerts(),
            sensors: SensorStore.getAllSensors(),
            zones: ZoneStore.getAllZones()
        }));
    }
});

module.exports = ThermonitorApp;
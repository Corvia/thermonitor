var Footer = require('./Footer.react');
var GraphSection = require('./GraphSection.react');
var Header = require('./Header.react');
var NotificationActions = require('../actions/NotificationActions');
var NotificationSection = require('./NotificationSection.react');
var NotificationStore = require('../stores/NotificationStore');
var React = require('react');
var SensorActions = require('../actions/SensorActions');
var SensorStore = require('../stores/SensorStore');
var ZoneActions = require('../actions/ZoneActions');
var ZoneSection = require('./ZoneSection.react');
var ZoneStore = require('../stores/ZoneStore');

var ThermonitorApp = React.createClass({
    componentDidMount: function() {
        NotificationStore.addChangeListener(this._onChange);
        SensorStore.addChangeListener(this._onChange);
        ZoneStore.addChangeListener(this._onChange);

        var intervalId = setInterval(this.requestData, 1000);
        this.setState($.extend(this.state, {
            intervalId: intervalId
        }));
    },

    componentWillUnmount: function() {
        NotificationStore.removeChangeListener(this._onChange);
        SensorStore.removeChangeListener(this._onChange);
        ZoneStore.removeChangeListener(this._onChange);
    },

    getInitialState: function() {
        return {
            intervalId: null,
            notifications: {},
            sensors: {},
            zones: {}
        };
    },

    render: function() {
        return (
            <div>
                <Header />
                <GraphSection sensors={this.state.sensors} />
                <ZoneSection zones={this.state.zones} />
                <NotificationSection notifications={this.state.notifications} />
                <Footer />
            </div>
        );
    },

    requestData: function() {
        ZoneActions.requestZones();
        SensorActions.requestSensors({
            zoneIds: Object.keys(this.state.zones)
        });
    },

    _onChange: function() {
        this.setState($.extend(this.state, {
            notifications: NotificationStore.getAllNotifications(),
            sensors: SensorStore.getAllSensors(),
            zones: ZoneStore.getAllZones()
        }));
    }
});

module.exports = ThermonitorApp;
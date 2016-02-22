var AlertActions = require('../actions/AlertActions');
var AlertStore = require('../stores/AlertStore');
var assign = require('object-assign');
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
        this.update();
        var intervalId = setInterval(this.update, 1000);
        var state = assign(this.state, {intervalId: intervalId});
        this.setState(state);
    },

    componentWillUnmount: function() {
        if (this.state.intervalId) {
            clearInterval(this.state.intervalId);
        }
    },

    getInitialState: function() {
        return {};
    },

    render: function() {
        return (
            <div>
                <Header />
                <GraphSection />
                <ZoneSection />
                <NotificationSection />
                <Footer />
            </div>
        );
    },

    update: function() {
        AlertActions.requestPagedAlerts(5, 0);
        SensorActions.requestSensors();
        ZoneActions.requestZones();
    }
});

module.exports = ThermonitorApp;
var _ = require('lodash');
var Alert = require('./Alert.react');
var AlertStore = require('../stores/AlertStore');
var React = require('react');

function getState() {
    return {
        alerts: _.sortByOrder(AlertStore.getAllAlerts(), ['date'], ['desc'])
    };
}

var NotificationSection = React.createClass({
    componentDidMount: function() {
        AlertStore.addChangeListener(this._onAlertStoreChange);
    },

    componentWillUnmount: function() {
        AlertStore.removeChangeListener(this._onAlertStoreChange);
    },

    getInitialState: function() {
        return getState();
    },

    render: function() {
        var alertNodes = this.state.alerts.map(function(alert) {
            return <Alert key={alert.id} alert={alert} />;
        });

        if (alertNodes.length === 0) {
            alertNodes = <h4>There are no notifications to display.</h4>
        }

        return (
            <div className="container notifications">
                <h2>Notification Activity</h2>
                <hr />
                {alertNodes}
            </div>
        );
    },

    _onAlertStoreChange: function() {
        this.setState(getState());
    }
});

module.exports = NotificationSection;
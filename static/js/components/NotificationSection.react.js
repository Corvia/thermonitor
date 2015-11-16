var Alert = require('./Alert.react')
var React = require('react');

var NotificationSection = React.createClass({
    render: function() {
        var alertNodes = [];
        for (var alertId in this.props.alerts) {
            var alert = this.props.alerts[alertId];
            alertNodes.push(<Alert key={alert.id} alert={alert} />);
        }
        return (
            <div className="container notifications">
                <h2>Notification Activity</h2>
                <hr />
                {alertNodes}
            </div>
        );
    }
});

module.exports = NotificationSection;
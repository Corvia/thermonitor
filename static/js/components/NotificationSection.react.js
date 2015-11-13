var Notification = require('./Notification.react')
var React = require('react');

var NotificationSection = React.createClass({
    render: function() {
        var notificationNodes = [];
        for (var notificationId in this.props.notifications) {
            var notification = this.props.notifications[notificationId];
            notificationNodes.push(<Notification key={notification.id} notification={notification} />);
        }
        return (
            <div className="container notifications">
                <h2>Notification Activity</h2>
                <hr />
                {notificationNodes}
            </div>
        );
    }
});

module.exports = NotificationSection;
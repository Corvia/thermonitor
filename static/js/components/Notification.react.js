var React = require('react');

var Notification = React.createClass({
    render: function() {
        var datetime = moment(this.props.notification.date, 'YYYY-MM-DDTH:m:s.SSSSSZ');
        var dateString = datetime.format('MMMM Do, YYYY')
        var timeString = datetime.format('h:mm a')
        var relativeTimeString = datetime.fromNow();
        return (
            <div className="row">
                <div className="col-md-2 datetime">{dateString} <span className="mute">@</span> {timeString}</div>
                <div className="col-md-8"><span className="bright">{message}</span> <span className="mute">an email has been sent to</span> {notification.recipients}</div>
                <div className="col-md-2 mute">{relativeTimeString}</div>
            </div>
        );
    }
});

module.exports = Notification;
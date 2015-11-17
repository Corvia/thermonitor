var moment = require('moment');
var React = require('react');

var Notification = React.createClass({
    render: function() {
        var datetime = moment(this.props.alert.date, 'YYYY-MM-DDTH:m:s.SSSSSZ');
        var dateString = datetime.format('L')
        var timeString = datetime.format('h:mm a')
        var relativeTimeString = datetime.fromNow();

        var recipientsDiv = null;
        if (this.props.alert.recipients) {
            var alertClass = '';
            switch (this.props.alert.alert_class.toLowerCase()) {
                case 'email':
                    alertClass = 'an email';
                    break;
            }

            recipientsDiv = <div className="col-md-8"><span className="bright">{this.props.alert.message}</span> <span className="mute">{alertClass} has been sent to</span> {this.props.alert.recipients}</div>
        }
        else {
            recipientsDiv = <div className="col-md-8"><span className="bright">{this.props.alert.message}</span></div>
        }

        return (
            <div className="row">
                <div className="col-md-2 datetime">{dateString} <span className="mute">@</span> {timeString}</div>
                {recipientsDiv}
                <div className="col-md-2 mute">{relativeTimeString}</div>
            </div>
        );
    }
});

module.exports = Notification;
var moment = require('moment');
var React = require('react');

function getCurrentDateTime() {
    // TODO Support other locales. :us:
    var now = moment();
    return {
        now: now,
        dateString: now.format('MMMM Do, YYYY'),
        timeString: now.format('h:mm a')
    };
}

var Header = React.createClass({
    update: function() {
        this.setState($.extend(this.state, getCurrentDateTime()));
    },

    getInitialState: function() {
        return getCurrentDateTime();
    },

    componentDidMount: function() {
        var intervalId = setInterval(this.update, 1000);
        var state = $.extend(this.state, {intervalId: intervalId});
        this.setState(state);
    },

    render: function() {
        return (
            <div id="Header">
                <div className="container">
                    <header>
                        <span className="logo"></span>
                        <span className="current-datetime">
                            <span className="date">{this.state.dateString}</span>
                            <span className="time">{this.state.timeString}</span>
                        </span>
                        <h1>Temperature Status</h1>
                    </header>
                </div>
            </div>
        );
    }
});

module.exports = Header;
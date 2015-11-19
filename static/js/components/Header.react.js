var assign = require('object-assign');
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
    componentDidMount: function() {
        var intervalId = setInterval(this.update, 1000);
        var state = assign(this.state, {intervalId: intervalId});
        this.setState(state);
    },

    componentWillUnmount: function() {
        SensorStore.removeChangeListener(this._onSensorStoreChange);

        if (this.state.intervalId) {
            clearInterval(this.state.intervalId);
        }
    },

    getInitialState: function() {
        return getCurrentDateTime();
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
    },

    update: function() {
        var state = assign(this.state, getCurrentDateTime());
        this.setState(state);
    }
});

module.exports = Header;
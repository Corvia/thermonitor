var React = require('react');

var Sensor = React.createClass({
    render: function() {
        var progressBarStyle = {
            width: '40%'
        };
        return (
            <div className="sensor col-md-2">
                <div className="progress vertical">
                    <div className="progress-bar progress-bar-info progress-bar-striped active"
                        role="progressbar"
                        aria-valuenow="{this.props.sensor.latest_value}"
                        aria-valuemin="0"
                        aria-valuemax="100"
                        style={progressBarStyle} />
                </div>
                <span className="gauge-temp">{this.props.sensor.latest_value}° F</span>
                <span className="gauge-label">{this.props.sensor.name}</span>
            </div>
        );
    }
});

module.exports = Sensor;
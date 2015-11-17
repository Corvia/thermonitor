var React = require('react');
var Sensor = require('./Sensor.react')

var SensorList = React.createClass({
    render: function() {
        var sensorNodes = [];
        for (var sensorId in this.props.sensors) {
            var sensor = this.props.sensors[sensorId];
            sensorNodes.push(<Sensor key={sensor.guid} sensor={sensor} />);
        }
        return (
            <div className="sensorList row gauges">
                {sensorNodes}
            </div>
        );
    }
});

module.exports = SensorList;
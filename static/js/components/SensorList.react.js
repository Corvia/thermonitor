var React = require('react');
var Sensor = require('./Sensor.react')

var SensorList = React.createClass({
    render: function() {
        var sensorNodes = this.props.sensors.map(function(sensor) {
            return <Sensor key={sensor.guid} sensor={sensor} />;
        });

        if (sensorNodes.length === 0) {
            var style = {marginLeft: '15px'};
            sensorNodes = <h4 style={style}>There are no sensors to display.</h4>
        }

        return (
            <div className="sensorList row gauges">
                {sensorNodes}
            </div>
        );
    }
});

module.exports = SensorList;
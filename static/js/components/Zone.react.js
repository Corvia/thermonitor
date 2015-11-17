var React = require('react');
var SensorList = require('./SensorList.react')
var SensorStore = require('../stores/SensorStore')

var Zone = React.createClass({
    render: function() {
        var filters = {zoneIds: [this.props.zone.id]};
        var sensors = SensorStore.getFilteredSensors(filters);
        return (
            <div className="zone">
                <h2>{this.props.zone.name}</h2>
                <hr />
                <SensorList sensors={sensors} />
            </div>
        );
    }
});

module.exports = Zone;
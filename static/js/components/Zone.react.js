var _ = require('lodash');
var React = require('react');
var SensorList = require('./SensorList.react');
var SensorStore = require('../stores/SensorStore');

function getState(filters) {
    return {
        sensors: _.sortByOrder(
            SensorStore.getFilteredSensors(filters),
            ['name'],
            ['asc']
        )
    };
}

var Zone = React.createClass({
    componentDidMount: function() {
        SensorStore.addChangeListener(this._onSensorStoreChange);
    },

    componentWillUnmount: function() {
        SensorStore.removeChangeListener(this._onSensorStoreChange);

        if (this.state.intervalId) {
            clearInterval(this.state.intervalId);
        }
    },

    getInitialState: function() {
        return getState(this._getSensorFilters());
    },

    render: function() {
        return (
            <div className="zone">
                <h2>{this.props.zone.name}</h2>
                <hr />
                <SensorList sensors={this.state.sensors} />
            </div>
        );
    },

    _getSensorFilters: function() {
        return {zoneIds: [this.props.zone.id]};
    },

    _onSensorStoreChange: function() {
        this.setState(getState(this._getSensorFilters()));
    }
});

module.exports = Zone;
var _ = require('lodash');
var React = require('react');
var Zone = require('./Zone.react');
var ZoneStore = require('../stores/ZoneStore');

function getState() {
    return {
        zones: _.sortByOrder(ZoneStore.getAllZones(), ['name'], ['asc'])
    };
}

var ZoneSection = React.createClass({
    componentDidMount: function() {
        ZoneStore.addChangeListener(this._onZoneStoreChange);
    },

    componentWillUnmount: function() {
        ZoneStore.removeChangeListener(this._onZoneStoreChange);
    },

    getInitialState: function() {
        return getState()
    },

    render: function() {
        var zoneNodes = this.state.zones.map(function(zone) {
            return <Zone key={zone.id} zone={zone} />;
        });

        if (zoneNodes.length === 0) {
            zoneNodes = <h2>There are no zones to display.</h2>
        }

        return (
            <div className="zoneSection container">
                {zoneNodes}
            </div>
        );
    },

    _onZoneStoreChange: function() {
        this.setState(getState());
    }
});

module.exports = ZoneSection;
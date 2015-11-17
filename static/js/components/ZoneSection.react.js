var React = require('react');
var Zone = require('./Zone.react')

var ZoneSection = React.createClass({
    render: function() {
        var zoneNodes = [];
        for (zoneId in this.props.zones) {
            var zone = this.props.zones[zoneId];
            zoneNodes.push(<Zone key={zone.id} zone={zone} />);
        }

        if (zoneNodes.length === 0) {
            zoneNodes = <h2>No zones have been added.</h2>
        }

        return (
            <div className="zoneSection container">
                {zoneNodes}
            </div>
        );
    }
});

module.exports = ZoneSection;
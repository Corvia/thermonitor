var React = require('react');
var Zone = require('./Zone.react')

var ZoneSection = React.createClass({
    render: function() {
        var zoneNodes = [];
        for (zoneId in this.props.zones) {
            var zone = this.props.zones[zoneId];
            zoneNodes.push(<Zone key={zone.id} zone={zone} />);
        }
        return (
            <div className="zoneSection container">
                {zoneNodes}
            </div>
        );
    }
});

module.exports = ZoneSection;
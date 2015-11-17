var React = require('react');

var Footer = React.createClass({
    render: function() {
        return (
            <div className="container footer">
                <hr />
                <p className="footer-text">thermonitor is built by Corvia Technologies and is released as open-source software.</p>
            </div>
        );
    }
});

module.exports = Footer;
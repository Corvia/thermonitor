var React = require('react');

var Footer = React.createClass({
    render: function() {
        return (
            <div className="container footer">
                <hr />
                <p className="footer-text">
                    thermonitor is built by Corvia Technologies and is&nbsp;
                    <a href="https://github.com/Corvia/thermonitor" target="_blank">released as open-source software</a>.
                </p>
            </div>
        );
    }
});

module.exports = Footer;
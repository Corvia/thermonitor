var ThermonitorDispatcher = require('../dispatcher/ThermonitorDispatcher');
var AlertConstants = require('../constants/AlertConstants');

var AlertActions = {
    receiveAlert: function(alert) {
        ThermonitorDispatcher.dispatch({
            actionType: AlertConstants.ALERT_RECEIVE_SINGLE,
            alert: alert
        });
    },

    receiveAlerts: function(alerts) {
        ThermonitorDispatcher.dispatch({
            actionType: AlertConstants.ALERT_RECEIVE_MANY,
            alerts: alerts
        });
    },

    receivePagedAlerts: function(pagedAlerts) {
        ThermonitorDispatcher.dispatch({
            actionType: AlertConstants.ALERT_RECEIVE_PAGED,
            pagedAlerts: pagedAlerts
        });
    },

    requestAlert: function(id) {
        ThermonitorDispatcher.dispatch({
            actionType: AlertConstants.ALERT_REQUEST_SINGLE,
            id: id
        });
        
        var self = this;
        $.ajax({
            url: 'api/v1/alerts/' + id + '/',
            type: 'GET',
            cache: false,
            success: function(data) {
                self.receiveAlert(data);
            }
        });
    },

    requestAlerts: function(filters) {
        ThermonitorDispatcher.dispatch({
            actionType: AlertConstants.ALERT_REQUEST_MANY,
            filters: filters
        });
        
        var self = this;
        $.ajax({
            url: 'api/v1/alerts/',
            type: 'GET',
            data: filters,
            cache: false,
            success: function(data) {
                self.receiveAlerts(data);
            }
        });
    },

    requestPagedAlerts: function(limit, offset, filters) {
        ThermonitorDispatcher.dispatch({
            actionType: AlertConstants.ALERT_REQUEST_PAGED,
            limit: limit,
            offset: offset,
            filters: filters
        });
        
        var self = this;
        var data = $.extend(filters || {}, {
            limit: limit,
            offset: offset
        });
        $.ajax({
            url: 'api/v1/alerts/',
            type: 'GET',
            data: data,
            cache: false,
            success: function(data) {
                self.receivePagedAlerts(data);
            }
        });
    }
};

module.exports = AlertActions;
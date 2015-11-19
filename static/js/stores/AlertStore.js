var _ = require('lodash');
var AlertConstants = require('../constants/AlertConstants');
var assign = require('object-assign');
var EventEmitter = require('events').EventEmitter;
var ThermonitorDispatcher = require('../dispatcher/ThermonitorDispatcher');

var CHANGE_EVENT = 'change';

var _alerts = [];

function createAlert(alert) {
    _alerts.push(alert);
    AlertStore.emitChange();
}

function updateAlert(alert) {
    var index = _.findIndex(_alerts, 'id', alert.id);
    
    if (index < 0) {
        _alerts.push(alert);
    }
    else {
        _alerts[index] = assign(_alerts[index], alert);
    }

    AlertStore.emitChange();
}

var AlertStore = assign({}, EventEmitter.prototype, {
    getAllAlerts: function() {
        return _alerts;
    },

    /**
     * Gets a filtered collection of the store's Alert object representations.
     * @param filters {object} An object containing the filters. The following
     *      properties may be included:
     *      alertIds: An array of Alert IDs. If included, only Alerts with
     *          matching IDs will be included in the result set.
     *      alertIds: An array of Sensor IDs. If included, only Alerts
     *          associated with matching Sensors will be included in the result
     *          set.
     * @returns {Object} A filtered collection of the store's Alert object
     *      representations.
     */
    getFilteredAlerts: function(filters) {
        if (!filters || (!filters.alertIds && !filters.sensorIds)) {
            return _alerts;
        }

        var getSensorId = function(alert) {
            if (!alert || typeof alert.sensor !== 'string') {
                return null;
            }
            return parseInt(alert.sensor.split('/')
                .filter(function(e) { return !!e; })
                .pop());
        }

        var filteredAlerts = _alerts;
        if (Array.isArray(filters.alertIds) && filters.alertIds.length > 0) {
            filteredAlerts = filteredAlerts.filter(function(alert) {
                return filters.alertIds.indexOf(alert.id) >= 0;
            });
        }

        if (Array.isArray(filters.sensorIds) && filters.sensorIds.length > 0) {
            filteredAlerts = filteredAlerts.filter(function(alert) {
                var alertId = getSensorId(alert);
                return filters.sensorIds.indexOf(sensorId) >= 0;
            });
        }

        return filteredAlerts;
    },

    /**
     * Gets a paged and optionally filtered collection of the store's Alert
     * object representations.
     * @param limit {Number} The maximum number of Alerts to include in the
     *      result set.
     * @param offset {Number} The number of elements to skip before returning
     *      the result set.
     * @param filters {Object} An object containing the filters. See
     *      `getFilteredAlerts` for a description of the available filters.
     * @returns {Array} A paged and optionally filtered collection of the
     *      store's Alert object representations.
     */
    getPagedAlerts: function(limit, offset, filters) {
        var filteredAlerts = filters ?
            this.getFilteredAlerts(filters) :
            _alerts;

        return filteredAlerts.slice(offset, offset + limit);
    },

    /**
     * Gets an Alert object representation from the store by its ID.
     * @param {Number} The ID of the Alert to get.
     * @returns {Object} The Alert object representation whose ID is `id`, or
     *      `null` if the object does not exist.
     */
    getAlert: function(id) {
        var result = _alerts.filter(function(alert) {
            return alert.id === id;
        });

        return result.length > 0 ? result[0] : null;
    },

    emitChange: function() {
        this.emit(CHANGE_EVENT);
    },

    addChangeListener: function(callback) {
        this.on(CHANGE_EVENT, callback);
    },

    removeChangeListener: function(callback) {
        this.removeListener(CHANGE_EVENT, callback);
    },

    dispatcherIndex: ThermonitorDispatcher.register(function(payload) {
        if (!payload.actionType) {
            return true;
        }

        switch(payload.actionType) {
            case AlertConstants.ALERT_RECEIVE_MANY:
                payload.alerts.forEach(updateAlert);
                break;

            case AlertConstants.ALERT_RECEIVE_PAGED:
                payload.pagedAlerts.results.forEach(updateAlert);
                break;

            case AlertConstants.ALERT_RECEIVE_SINGLE:
                updateAlert(payload.alert);
                break;
        }

        return true;
    })
});

module.exports = AlertStore;
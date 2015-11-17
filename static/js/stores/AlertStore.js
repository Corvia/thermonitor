var ThermonitorDispatcher = require('../dispatcher/ThermonitorDispatcher');
var EventEmitter = require('events').EventEmitter;
var AlertConstants = require('../constants/AlertConstants');
var assign = require('object-assign');

var CHANGE_EVENT = 'change';

var _alerts = {};

function createAlert(alert) {
    _alerts[alert.id] = alert;
}

function updateAlert(alert) {
    _alerts[alert.id] = alert;
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
        if (!filters || (
            !filters.hasOwnProperty('alertIds') &&
            !filters.hasOwnProperty('alertIds') &&
            !filters.hasOwnProperty('zoneIds'))) {
                return _alerts;
        }

        var getSensorId = function(alert) {
            if (!alert ||
                !alert.hasOwnProperty('alert') ||
                typeof alert.alert !== 'string') {
                    return null;
            }
            return parseInt(alert.alert.split('/')
                .filter(function(e) { return !!e; })
                .pop());
        }

        var isExcludedByAlertIdsFilter;
        if (!filters.hasOwnProperty('alertIds') ||
            !Array.isArray(filters.alertIds) ||
            filters.alertIds.length === 0) {
                isExcludedByAlertIdsFilter = function(alert) {
                    return false;
                };
        }
        else {
            isExcludedByAlertIdsFilter = function(alert) {
                return filters.alertIds.indexOf(alert.id) < 0;
            }
        }

        var isExcludedBySensorIdsFilter;
        if (!filters.hasOwnProperty('sensorIds') ||
            !Array.isArray(filters.sensorIds) ||
            filters.sensorIds.length === 0) {
                isExcludedBySensorIdsFilter = function(alert) {
                    return false;
                };
        }
        else {
            isExcludedBySensorIdsFilter = function(alert) {
                var sensorId = getSensorId(alert);
                return filters.sensorIds.indexOf(sensorId) < 0;
            }
        }

        var result = {};
        for (var alertId in _alerts) {
            var alert = _alerts[alertId];
            if (isExcludedByAlertIdsFilter(alert) ||
                isExcludedBySensorIdsFilter(alert)) {
                    continue;
            }

            result[alert.id] = alert;
        }

        return result;
    },

    /**
     * Gets a paged and optionally filtered collection of the store's Sensor
     * object representations.
     * @param limit {Number} The maximum number of Sensors to include in the
     *      result set.
     * @param offset {Number} The number of elements to skip before returning
     *      the result set.
     * @param filters {Object} An object containing the filters. See
     *      `getFilteredSensors` for a description of the available filters.
     * @returns {Array} A paged and optionally filtered collection of the
     *      store's Sensor object representations.
     */
    getPagedAlerts: function(limit, offset, filters) {
        var filteredAlerts = filters ?
            this.getFilteredAlerts(filters) :
            _alerts;

        var result = {};
        var counter = 0;
        for (var alertId in filteredAlerts) {
            if (counter >= offset + limit) {
                break;
            }

            if (counter >= offset) {
                result[alertId] = filteredAlerts[alertId];
            }
            
            counter++;
        }

        return result;
    },

    /**
     * Gets an Alert object representation from the store by its ID.
     * @param {Number} The ID of the Alert to get.
     * @returns {Object} The Alert object representation whose ID is `id`, or
     *      `null` if the object does not exist.
     */
    getAlert: function(id) {
        if (!_alerts.hasOwnProperty(id)) {
            return null;
        }

        return _alerts[id];
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
                updateSensor(payload.alert);
                break;
        }

        return true;
    })
});

module.exports = AlertStore;
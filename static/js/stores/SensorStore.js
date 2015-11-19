var _ = require('lodash');
var assign = require('object-assign');
var EventEmitter = require('events').EventEmitter;
var SensorActions = require('../actions/SensorActions');
var SensorConstants = require('../constants/SensorConstants');
var ThermonitorDispatcher = require('../dispatcher/ThermonitorDispatcher');

var CHANGE_EVENT = 'change';

var _sensors = [];

function createSensor(sensor) {
    _sensors.push(sensor);
    SensorStore.emitChange();
}

function destroySensor(sensor) {
    var index = _.findIndex(_sensors, 'id', sensor.id);
    _sensors.splice(index, 1);
    SensorStore.emitChange();
}

function updateSensor(sensor) {
    var index = _.findIndex(_sensors, 'id', sensor.id);
    
    if (index < 0) {
        _sensors.push(sensor);
    }
    else {
        _sensors[index] = assign(_sensors[index], sensor);
    }
    
    SensorStore.emitChange();
}

var SensorStore = assign({}, EventEmitter.prototype, {
    getAllSensors: function() {
        return _sensors;
    },

    /**
     * Gets a filtered collection of the store's Sensor object representations.
     * @param filters {object} An object containing the filters. The following
     *      properties may be included:
     *      sensorIds: An array of Sensor IDs. If included, only Sensors with
     *          matching IDs will be returned.
     *      zoneIds: An array of Zone IDs. If included, only Sensors that belong
     *          to the specified Zones will be included.
     * @returns {Object} A filtered collection of the store's Sensor object
     *      representations.
     */
    getFilteredSensors: function(filters) {
        if (!filters || (!filters.sensorIds && !filters.zoneIds)) {
            return _sensors;
        }

        var getZoneId = function(sensor) {
            if (!sensor || typeof sensor.zone !== 'string') {
                return null;
            }
            return parseInt(sensor.zone.split('/')
                .filter(function(e) { return !!e; })
                .pop());
        }

        var filteredSensors = _sensors;
        if (Array.isArray(filters.sensorIds) && filters.sensorIds.length > 0) {
            filteredSensors = filteredSensors.filter(function(sensor) {
                return filters.sensorIds.indexOf(sensor.id) >= 0;
            });
        }

        if (Array.isArray(filters.zoneIds) && filters.zoneIds.length > 0) {
            filteredSensors = filteredSensors.filter(function(sensor) {
                var zoneId = getZoneId(sensor);
                return filters.zoneIds.indexOf(zoneId) >= 0;
            });
        }

        return filteredSensors;
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
    getPagedSensors: function(limit, offset, filters) {
        var filteredSensors = filters ?
            this.getFilteredSensors(filters) :
            _sensors;

        return filteredSensors.slice(offset, offset + limit);
    },

    /**
     * Gets a Sensor object representation from the store by its ID.
     * @param {Number} The ID of the Sensor to get.
     * @returns {Object} The Sensor object representation whose ID is `id`, or
     *      `null` if the object does not exist.
     */
    getSensor: function(id) {
        var result = _sensors.filter(function(sensor) {
            return sensor.id === id;
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
            case SensorConstants.SENSOR_CREATE:
                createSensor(payload.sensor);
                break;

            case SensorConstants.SENSOR_DESTROY:
                destroySensor(payload.sensor);
                break;

            case SensorConstants.SENSOR_RECEIVE_MANY:
                payload.sensors.forEach(updateSensor);
                break;

            case SensorConstants.SENSOR_RECEIVE_PAGED:
                payload.pagedSensors.results.forEach(updateSensor);
                break;

            case SensorConstants.SENSOR_RECEIVE_SINGLE:
                updateSensor(payload.sensor);
                break;

            case SensorConstants.SENSOR_UPDATE:
                updateSensor(payload.sensor);
                break;

            default:
                break;
        }

        return true;
    })
});

module.exports = SensorStore;
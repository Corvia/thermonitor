var ThermonitorDispatcher = require('../dispatcher/ThermonitorDispatcher');
var EventEmitter = require('events').EventEmitter;
var SensorConstants = require('../constants/SensorConstants');
var assign = require('object-assign');

var CHANGE_EVENT = 'change';

var _sensors = {};

function createSensor(sensor) {
    _sensors[sensor.id] = sensor;
}

function destroySensor(id) {
    delete _sensors[id];
}

function updateSensor(sensor) {
    _sensors[sensor.id] = sensor;
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
        if (!filters || (
            !filters.hasOwnProperty('sensorIds') &&
            !filters.hasOwnProperty('zoneIds'))) {
                return _sensors;
        }

        var getZoneId = function(sensor) {
            if (!sensor ||
                !sensor.hasOwnProperty('zone') ||
                typeof sensor.zone !== 'string') {
                    return null;
            }
            return parseInt(sensor.zone.split('/')
                .filter(function(e) { return !!e; })
                .pop());
        }

        var isExcludedBySensorIdsFilter;
        if (!filters.hasOwnProperty('sensorIds') ||
            !Array.isArray(filters.sensorIds) ||
            filters.sensorIds.length === 0) {
                isExcludedBySensorIdsFilter = function(sensor) {
                    return false;
                };
        }
        else {
            isExcludedBySensorIdsFilter = function(sensor) {
                return filters.sensorIds.indexOf(sensor.id) >= 0;
            }
        }

        var isExcludedByZoneIdsFilter;
        if (!filters.hasOwnProperty('zoneIds') ||
            !Array.isArray(filters.zoneIds) ||
            filters.zoneIds.length === 0) {
                isExcludedByZoneIdsFilter = function(sensor) {
                    return false;
                };
        }
        else {
            isExcludedByZoneIdsFilter = function(sensor) {
                var zoneId = getZoneId(sensor);
                return filters.zoneIds.indexOf(zoneId) < 0;
            }
        }

        var result = {};
        for (var sensorId in _sensors) {
            var sensor = _sensors[sensorId];
            if (isExcludedBySensorIdsFilter(sensor) ||
                isExcludedByZoneIdsFilter(sensor)) {
                    continue;
            }

            result[sensor.id] = sensor;
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
    getPagedSensors: function(limit, offset, filters) {
        var filteredSensors = filters ?
            this.getFilteredSensors(filters) :
            _sensors;

        var result = {};
        var counter = 0;
        for (var sensorId in filteredSensors) {
            if (counter >= offset + limit) {
                break;
            }

            if (counter >= offset) {
                result[sensorId] = filteredSensors[sensorId];
            }
            
            counter++;
        }

        return result;
    },

    /**
     * Gets a Sensor object representation from the store by its ID.
     * @param {Number} The ID of the Sensor to get.
     * @returns {Object} The Sensor object representation whose ID is `id`, or
     *      `null` if the object does not exist.
     */
    getSensor: function(id) {
        if (!_sensors.hasOwnProperty(id)) {
            return null;
        }

        return _sensors[id];
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
                destroySensor(payload.sensor.id);
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
        }

        SensorStore.emitChange();

        return true;
    })
});

module.exports = SensorStore;
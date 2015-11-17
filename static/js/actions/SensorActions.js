var ThermonitorDispatcher = require('../dispatcher/ThermonitorDispatcher');
var SensorConstants = require('../constants/SensorConstants');

var SensorActions = {
    createSensor: function(sensor) {
        ThermonitorDispatcher.dispatch({
            actionType: SensorConstants.SENSOR_CREATE,
            sensor: sensor
        });
    },

    destroySensor: function(sensor) {
        ThermonitorDispatcher.dispatch({
            actionType: SensorConstants.SENSOR_DESTROY,
            sensor: sensor
        });
    },

    receiveSensor: function(sensor) {
        ThermonitorDispatcher.dispatch({
            actionType: SensorConstants.SENSOR_RECEIVE_SINGLE,
            sensor: sensor
        });
    },

    receiveSensors: function(sensors) {
        ThermonitorDispatcher.dispatch({
            actionType: SensorConstants.SENSOR_RECEIVE_MANY,
            sensors: sensors
        });
    },

    receivePagedSensors: function(pagedSensors) {
        ThermonitorDispatcher.dispatch({
            actionType: SensorConstants.SENSOR_RECEIVE_PAGED,
            pagedSensors: pagedSensors
        });
    },

    requestSensor: function(id) {
        ThermonitorDispatcher.dispatch({
            actionType: SensorConstants.SENSOR_REQUEST_SINGLE,
            id: id
        });
        
        var self = this;
        $.ajax({
            url: 'api/v1/sensors/' + id + '/',
            type: 'GET',
            cache: false,
            success: function(data) {
                self.receiveSensor(data);
            }
        });
    },

    requestSensors: function(filters) {
        ThermonitorDispatcher.dispatch({
            actionType: SensorConstants.SENSOR_REQUEST_MANY,
            filters: filters
        });
        
        var self = this;
        $.ajax({
            url: 'api/v1/sensors/',
            type: 'GET',
            data: filters,
            cache: false,
            success: function(data) {
                self.receiveSensors(data);
            }
        });
    },

    requestPagedSensors: function(limit, offset, filters) {
        ThermonitorDispatcher.dispatch({
            actionType: SensorConstants.SENSOR_REQUEST_PAGED,
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
            url: 'api/v1/sensors/',
            type: 'GET',
            data: data,
            cache: false,
            success: function(data) {
                self.receivePagedSensors(data);
            }
        });
    },

    updateSensor: function(sensor) {
        ThermonitorDispatcher.dispatch({
            actionType: SensorConstants.SENSOR_UPDATE,
            sensor: sensor
        });
    }
};

module.exports = SensorActions;
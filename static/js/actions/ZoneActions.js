var assign = require('object-assign');
var ThermonitorDispatcher = require('../dispatcher/ThermonitorDispatcher');
var ZoneConstants = require('../constants/ZoneConstants');

var ZoneActions = {
    receiveZone: function(zone) {
        ThermonitorDispatcher.dispatch({
            actionType: ZoneConstants.ZONE_RECEIVE_SINGLE,
            zone: zone
        });
    },

    receiveZones: function(zones) {
        ThermonitorDispatcher.dispatch({
            actionType: ZoneConstants.ZONE_RECEIVE_MANY,
            zones: zones
        });
    },

    receivePagedZones: function(pagedZones) {
        ThermonitorDispatcher.dispatch({
            actionType: ZoneConstants.ZONE_RECEIVE_PAGED,
            pagedZones: pagedZones
        });
    },

    requestZone: function(id) {
        ThermonitorDispatcher.dispatch({
            actionType: ZoneConstants.ZONE_REQUEST_SINGLE,
            id: id
        });
        
        var self = this;
        $.ajax({
            url: 'api/v1/zones/' + id + '/',
            type: 'GET',
            cache: false,
            success: function(data) {
                self.receiveZone(data);
            }
        });
    },

    requestZones: function(filters) {
        ThermonitorDispatcher.dispatch({
            actionType: ZoneConstants.ZONE_REQUEST_MANY,
            filters: filters
        });
        
        var self = this;
        $.ajax({
            url: 'api/v1/zones/',
            type: 'GET',
            data: filters,
            cache: false,
            success: function(data) {
                self.receiveZones(data);
            }
        });
    },

    requestPagedZones: function(limit, offset, filters) {
        ThermonitorDispatcher.dispatch({
            actionType: ZoneConstants.ZONE_REQUEST_PAGED,
            limit: limit,
            offset: offset,
            filters: filters
        });
        
        var self = this;
        var data = assign(filters || {}, {
            limit: limit,
            offset: offset
        });
        $.ajax({
            url: 'api/v1/zones/',
            type: 'GET',
            data: data,
            cache: false,
            success: function(data) {
                self.receivePagedZones(data);
            }
        });
    },

    updateZone: function(zone) {
        ThermonitorDispatcher.dispatch({
            actionType: ZoneConstants.ZONE_UPDATE,
            zone: zone
        })
    }
};

module.exports = ZoneActions;
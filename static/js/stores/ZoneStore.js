var _ = require('lodash');
var assign = require('object-assign');
var EventEmitter = require('events').EventEmitter;
var ThermonitorDispatcher = require('../dispatcher/ThermonitorDispatcher');
var ZoneConstants = require('../constants/ZoneConstants');

var CHANGE_EVENT = 'change';

var _zones = [];

function createZone(zone) {
    _zones.push(zone);
    ZoneStore.emitChange();
}

function updateZone(zone) {
    var index = _.findIndex(_zones, 'id', zone.id);
    var target = _zones.filter(function(e) {
        return zone.id === e.id;
    });

    if (index < 0) {
        _zones.push(zone);
    }
    else {
        _zones[index] = assign(_zones[index], zone);
    }

    ZoneStore.emitChange();
}

var ZoneStore = assign({}, EventEmitter.prototype, {
    getAllZones: function() {
        return _zones;
    },

    /**
     * Gets a filtered collection of the store's Zone object representations.
     * @param filters {object} An object containing the filters. The following
     *      properties may be included:
     *      zoneIds: An array of Zone IDs. If included, only Zones with matching
     *          IDs will be returned.
     * @returns {Object} A filtered collection of the store's Zone object
     *      representations.
     */
    getFilteredZones: function(filters) {
        if (!filters || !filters.zoneIds) {
            return _zones;
        }

        var filteredZones = _zones;
        if (Array.isArray(filters.zoneIds) && filters.zoneIds.length > 0) {
            filteredZones = filteredZones.filter(function(zone) {
                return filters.zoneIds.indexOf(zone.id) >= 0;
            });
        }

        return filteredZones;
    },

    /**
     * Gets a paged and optionally filtered collection of the store's Zone
     * object representations.
     * @param limit {Number} The maximum number of Zones to include in the
     *      result set.
     * @param offset {Number} The number of elements to skip before returning
     *      the result set.
     * @param filters {Object} An object containing the filters. See
     *      `getFilteredSensors` for a description of the available filters.
     * @returns {Array} A paged and optionally filtered collection of the
     *      store's Zone object representations.
     */
    getPagedZones: function(limit, offset, filters) {
        var filteredZones = filters ?
            this.getFilteredZones(filters) :
            _zones;

        return filteredZones.slice(offset, offset + limit);
    },

    /**
     * Gets a Zone object representation from the store by its ID.
     * @param {Number} The ID of the Zone to get.
     * @returns {Object} The Zone object representation whose ID is `id`, or
     *      `null` if the object does not exist.
     */
    getZone: function(id) {
        var result = _zones.filter(function(zone) {
            return zone.id === id;
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
            case ZoneConstants.ZONE_RECEIVE_MANY:
                payload.zones.forEach(updateZone);
                break;

            case ZoneConstants.ZONE_RECEIVE_PAGED:
                payload.pagedZones.results.forEach(updateZone);
                break;

            case ZoneConstants.ZONE_RECEIVE_SINGLE:
                updateZone(payload.zone);
                break;

            case ZoneConstants.ZONE_UPDATE:
                updateZone(zone);
                break;
        }

        return true;
    })
});

module.exports = ZoneStore;
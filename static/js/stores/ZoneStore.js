var ThermonitorDispatcher = require('../dispatcher/ThermonitorDispatcher');
var EventEmitter = require('events').EventEmitter;
var ZoneConstants = require('../constants/ZoneConstants');
var assign = require('object-assign');

var CHANGE_EVENT = 'change';

var _zones = {};

function updateZone(zone) {
    _zones[zone.id] = zone;
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
        if (!filters || !filters.hasOwnProperty('zoneIds')) {
                return _sensors;
        }

        var isExcludedByZoneIdsFilter;
        if (!filters.hasOwnProperty('zoneIds') ||
            !Array.isArray(filters.zoneIds) ||
            filters.zoneIds.length === 0) {
                isExcludedByZoneIdsFilter = function(zone) {
                    return false;
                };
        }
        else {
            isExcludedByZoneIdsFilter = function(zone) {
                return filters.zoneIds.indexOf(zone.id) < 0;
            }
        }

        var result = {};
        for (var zoneId in _zones) {
            var zone = _zones[zoneId];
            if (isExcludedByZoneIdsFilter(zone)) {
                    continue;
            }

            result[zone.id] == zone;
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
    getPagedZones: function(limit, offset, filters) {
        var filteredZones = filters ?this.getFilteredZones(filters) : _zones;

        var result = {};
        var counter = 0;
        for (var zoneId in filteredZones) {
            if (counter >= offset + limit) {
                break;
            }

            if (counter >= offset) {
                result[zoneId] = filteredZones[zoneId];
            }
            
            counter++;
        }

        return result;
    },

    /**
     * Gets a Zone object representation from the store by its ID.
     * @param {Number} The ID of the Zone to get.
     * @returns {Object} The Zone object representation whose ID is `id`, or
     *      `null` if the object does not exist.
     */
    getZone: function(id) {
        if (!_zones.hasOwnProperty(id)) {
            return null;
        }

        return _zones[id];
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

        ZoneStore.emitChange();

        return true;
    })
});

module.exports = ZoneStore;
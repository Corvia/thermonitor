var ThermonitorDispatcher = require('../dispatcher/ThermonitorDispatcher');
var EventEmitter = require('events').EventEmitter;
var NotificationConstants = require('../constants/NotificationConstants');
var assign = require('object-assign');

var CHANGE_EVENT = 'change';

var _notifications = {};

var NotificationStore = assign({}, EventEmitter.prototype, {
    getAllNotifications: function() {
        return _notifications;
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
        }

        return true;
    })
});

module.exports = NotificationStore;
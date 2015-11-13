var ThermonitorDispatcher = require('../dispatcher/ThermonitorDispatcher');
var NotificationConstants = require('../constants/NotificationConstants');

var NotificaitonActions = {
    updateNotification: function(notification) {
        ThermonitorDispatcher.dispatch({
            actionType: NotificationConstants.ZONE_UPDATE,
            notification: notification
        })
    }
};

module.exports = NotificaitonActions;
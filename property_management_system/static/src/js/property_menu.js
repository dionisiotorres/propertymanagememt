odoo.define('property_management_system.SwitchPropertyMenu', function(require) {
    "use strict";
        var Widget = require('web.Widget');
        var SwitchPropertyMenu = require('property_management_system.SwitchPropertyMenu');
        var PropertyMenu = Widget.extend({
            custom_events: {
                valuechange: '_onValueChange'
            },
            init: function (parent, menu_data) {
                var self = this;
                console.log(self);
                this._super.apply(this, arguments);
            },
            start: function () {
                console.log(this);
                this.SwitchPropertyMenu = new SwitchPropertyMenu(this);
                var def = this.SwitchPropertyMenu.appendTo(this.$el);
                return Promise.all([def, this._super.apply(this, arguments)]);
            },
            _onValueChange: function(event) {
               console.log(event);
            },
        })
        
        this.trigger_up('valuechange', {value: someValue});
    return {
            'PropertyMenu': PropertyMenu,
        };
    }); 
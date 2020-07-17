odoo.define('property_management_system.PropertyMenu', function(require) {
    "use strict";
        var Widget = require('web.Widget');
        var config = require('web.config');
        var core = require('web.core');
        var session = require('web.session');
        var SystrayMenu = require('web.SystrayMenu');
        var _t = core._t;
        console.log('hello');
        var PropertyMenu = Widget.extend({
            template: 'PropertyMenu',
            events: {
                'click .dropdown-item[data-menu]': '_onClickMenu',
            },
            init: function () {
                this._super.apply(this, arguments);
                this.isMobile = config.device.isMobile;
                this._onClick = _.debounce(this._onClick, 1500, true);
                console.log("HI");
            },
            /**
            * @override
            */
            willStart: function () {
                console.log(session);
                return session.user_properties ? this._super() : $.Deferred().reject();
            },
            /**
             * @override
             */
            start: function () {
                var propertiesList = '';
                console.log('hello1');
                if (this.isMobile) {
                    propertiesList = '<li class="bg-info">' +
                        _t('Tap on the list to change property') + '</li>';
                }
                else {
                    this.$('.oe_topbar_name').text(session.user_properties.current_property[1]);
                }
                _.each(session.user_properties.allowed_properties, function(property) {
                    var a = '';
                    var isCurrentProperty = property[0] === session.user_properties.current_property[0];
                    if (isCurrentProperty) {
                        a = '<i class="fa fa-check mr8"></i>';
                    } else {
                        a = '<span style="margin-right: 24px;"/>';
                    }
                    propertiesList += '<a role="menuitemradio" aria-checked="' + isCurrentProperty + '" href="#" class="dropdown-item" data-menu="property" data-property-id="' +
                    property[0] + '">' + a + property[1] + '</a>';
                });
                this.$('.dropdown-menu').html(propertiesList);
                return this._super();
            },

            //--------------------------------------------------------------------------
            // Handlers
            //--------------------------------------------------------------------------

            /**
             * @private
             * @param {MouseEvent} ev
             */
            _onClickMenu: function (ev) {
                ev.preventDefault();
                var propertyID = $(ev.currentTarget).data('property-id');
                console.log('hello2');
                this._rpc({
                    model: 'res.users',
                    method: 'write',
                    args: [[session.uid], {'current_property_id': propertyID}],
                })
                .then(function() {
                    location.reload();
                });
            },
        });

    SystrayMenu.Items.push(PropertyMenu);

    return PropertyMenu;
});

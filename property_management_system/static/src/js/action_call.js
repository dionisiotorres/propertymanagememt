odoo.define('property_management_system.action_button', function (require) {
    "use strict";
    var core = require('web.core');
    var ListController = require('web.ListController');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var _t = core._t;
    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.find('.oe_action_button').click(this.proxy('action_def'));
            }
        },
        action_def: function () {
            console.log(event);
            var self = this
            var user = session.uid;
            var selection_id = [];
            var select_values = self.selectedRecords;
            var active_id = self.initialState.context.active_id;
            if (self.initialState.data) {
                for (var k = 0; k < self.initialState.data.length; k++) {
                    if (select_values) {
                        for (var i = 0; i < select_values.length; i++) {
                            if (self.initialState.data[k].id == select_values[i]) {
                                selection_id.push(self.initialState.data[k].data.id);
                            }
                        }
                    }
                }
            }
            rpc.query({
                model: 'pms.space.facilities',
                method: 'select_values',
                args: [[user], { 'id': user, 'active_id': active_id, 'selection_id': selection_id }],
            });
            rpc.query({
                model: 'pms.space.unit',
                method: 'do_action',
                args: [[user], { 'id': user, 'active_id': active_id }],
            }).then(function () {
                location.reload();
                return {
                    type: 'ir.actions.act_window',
                    res_model: "pms.space.unit",
                    res_id: active_id,
                    views: [[false, 'form']],
                    target: 'current',
                    context: {},
                }
            });
        },
    });
});
odoo.define('property_management_system.action_button', function(require) {
    "use strict";
    var core = require('web.core');
    var ListController = require('web.ListController');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var _t = core._t;
    ListController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.find('.oe_action_button').click(this.proxy('action_def'));
            }
        },
        action_def: function(){
            var self =this
            var user = session.uid;
            var selection_id = [];
            var active_id = self.initialState.context.active_id;
            if (self.initialState.data){
                for (var k=0; k < self.initialState.data.length; k++) {
                    for (var i=0; i < self.selectedRecords.length; i++){
                        if (self.initialState.data[k].id == self.selectedRecords[i])
                        {
                            selection_id.push(self.initialState.data[k].data.id);
                        }
                    }
                }
            }
            rpc.query({
                model:'pms.space.facilities',
                method: 'select_values',
                args: [[user],{'id':user,'active_id':active_id,'selection_id':selection_id}],
                }).then(function() {
                    location.reload();
                });
            },
    });
});
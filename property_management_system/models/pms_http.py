from odoo.http import request
import odoo
from odoo import models

class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        user = request.env.user
        res = super(Http, self).session_info()
        display_switch_property_menu = len(user.property_id) > 1
        res['property_id'] =  user.current_property_id.id if request.session.uid else None
        res['user_properties'] = {'current_property': (user.current_property_id.id, user.current_property_id.name), 'allowed_properties': [(pro.id, pro.name) for pro in user.property_id]} if display_switch_property_menu else False
        return res

from odoo import models, fields, api

class Users(models.Model):
    _inherit = "res.users"
    _description = 'Users'
    _inherits = {'res.partner': 'partner_id'}
    _order = 'name, login'

    current_property_id = fields.Many2one("pms.properties", string="Current Property")

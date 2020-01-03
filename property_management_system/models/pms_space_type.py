from odoo import models, fields, api


class PMSSpaceType(models.Model):
    _name = 'pms.space.type'
    _description = 'Space Type'

    name = fields.Char("Name", required=True, track_visibility=True)
    # property_id = fields.Many2one("pms.properties", "Property", required=True)
    # chargeable = fields.Boolean("Chargeable", track_visibility=True)
    # divisible = fields.Boolean("Divisible", track_visibility=True)
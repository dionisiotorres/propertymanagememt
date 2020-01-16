from odoo import models, fields, api


class PMSSpaceType(models.Model):
    _name = 'pms.space.type'
    _description = 'Space Type'
    _order = 'ordinal_no,name'

    name = fields.Char("Name", required=True, track_visibility=True)
    ordinal_no = fields.Integer("Order No", required=True)

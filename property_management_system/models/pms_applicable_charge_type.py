from odoo import models, fields, api


class PMSApplicableChargeType(models.Model):
    _name = 'pms.applicable.charge.type'
    _description = "Applicable Charge Type"
    _inherit = ['mail.thread']

    name = fields.Char("Description", required=True, track_visibility=True)
    charge_type = fields.Char("Floor Code",
                              required=True,
                              track_visibility=True)
    calculatedby = fields.Char("Floor Ref Code", track_visibility=True)

from odoo import models, fields, api


class PMSApplicableChargeType(models.Model):
    _name = 'pms.applicable.charge.type'
    _description = "Applicable Charge Type"
    _inherit = ['mail.thread']

    name = fields.Char("Description", required=True, track_visibility=True)
    charge_type = fields.Many2one("pms.charge_types",
                                  required=True,
                                  track_visibility=True)
    calculatedby = fields.Selection([('percent', 'Percentage'), ('fix', 'Fix'),
                                     ('area', 'Area'),
                                     ('meter_unit', 'Meter Unit')],
                                    "Calculated By",
                                    track_visibility=True)
    tax = fields.Float("Tax")
    active = fields.Boolean(default=True)

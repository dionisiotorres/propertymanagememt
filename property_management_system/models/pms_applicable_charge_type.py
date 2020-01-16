from odoo import models, fields, api


class PMSApplicableChargeType(models.Model):
    _name = 'pms.applicable.charge.type'
    _description = "Applicable Charge Type"
    _inherit = ['mail.thread']

    name = fields.Char("Charge Type", required=True, track_visibility=True)
    charge_type_id = fields.Many2one("pms.charge_types",
                                     'Main Charge Type',
                                     required=True,
                                     track_visibility=True)
    calculation_method_id = fields.Many2one('pms.calculation.method',
                                            "Calculation Method",
                                            track_visibility=True,
                                            required=True,
                                            store=True)
    is_apply_tax = fields.Boolean('Apply Tax', track_visibility=True)
    tax = fields.Float("Tax", track_visibility=True)
    # ordinal_no = fields.Integer("Ordinal No", store=True, required=True)
    active = fields.Boolean(default=True)

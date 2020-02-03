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
    billing_type = fields.Selection([('monthly', 'Monthly'),
                                     ('quarterly', 'Quarterly'),
                                     ('semi-annually', 'Semi-Annually')],
                                    "Billing Type",
                                    required=True,
                                    default='monthly',
                                    track_visibility=True)
    active = fields.Boolean(default=True)
    unit_charge_line = fields.One2many("pms.unit.charge.line",
                                       "applicable_charge_id",
                                       "Unit Charge Line")
    is_formula_meter = fields.Boolean("Use Formula Meter")
    fix_meter_rate = fields.Float("Fix Meter Rate")


class PMSUnitChargeLine(models.Model):
    _name = "pms.unit.charge.line"
    _description = "Unit Charge Line"

    name = fields.Char("Name")
    from_unit = fields.Float("From")
    to_unit = fields.Float("To")
    rate = fields.Float("Rate")
    applicable_charge_id = fields.Many2one("pms.applicable.charge.type",
                                           'Applicable Charge Type')

    def compute(self):
        if self.from_unit and self.to_unit and self.rate:
            self.name = "Rate " + str(self.rate) + "(From " + str(
                self.from_unit) + " Units To" + str(self.to_unit) + ")."
        else:
            self.name = "UNDEFINED"

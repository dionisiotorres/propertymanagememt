from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError


class PMSApplicableChargeType(models.Model):
    _name = 'pms.applicable.charge.type'
    _description = "Applicable Charge Type"
    _inherit = ['mail.thread']

    name = fields.Char("Charge Type", required=True, track_visibility=True)
    charge_type_id = fields.Many2one("pms.charge_types",
                                     'Main Charge Type',
                                     required=True,
                                     track_visibility=True)
    calculate_method_ids = fields.Many2many(
        'pms.calculation.method',
        "Calculation Method",
        related="charge_type_id.calculate_method_ids")
    calculation_method_id = fields.Many2one('pms.calculation.method',
                                            "Calculation Method",
                                            track_visibility=True,
                                            readonly=False,
                                            required=True,
                                            store=True)
    is_apply_tax = fields.Boolean('Apply Tax', default=True,track_visibility=True)
    tax_id = fields.Many2one("account.tax","Tax")
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
    use_formula = fields.Boolean("Use Formula")
    rate = fields.Float("Rate")
    source_type_id = fields.Many2one("pms.utilities.supply",
                                     "Source Type")
    is_meter = fields.Boolean("IsMeter",
                              default=False,
                              compute="compute_ismeter")
    sequence = fields.Integer(track_visibility=True)
    index = fields.Integer(compute='_compute_index')

    @api.one
    def _compute_index(self):
        cr, uid, ctx = self.env.args
        self.index = self._model.search_count(cr,uid,[('sequence','<',self.sequence)],context=ctx) + 1

    @api.one
    @api.depends('calculation_method_id')
    def compute_ismeter(self):
        if self.calculation_method_id:
            if self.calculation_method_id.name == 'MeterUnit':
                self.is_meter = True
            else:
                self.is_meter = False

    @api.model
    def create(self, values):
        charge_type_id = self.search([('name', '=', values['name'])])
        if charge_type_id:
            raise UserError(_("%s is already existed" % values['name']))
        return super(PMSApplicableChargeType, self).create(values)

    @api.multi
    def write(self, vals):
        if 'name' in vals:
            charge_type_id = self.search([('name', '=', vals['name'])])
            if charge_type_id:
                raise UserError(_("%s is already existed" % vals['name']))
        return super(PMSApplicableChargeType, self).write(vals)


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

class PMSBaseCharge(models.Model):
    _name = "pms.base.charge"
    _description = "sequence,name"

    name = fields.Char("Name")
    description = fields.Text("Description")
    sequence = fields.Integer(track_visibility=True)
    index = fields.Integer(compute='_compute_index')
    base_type_id = fields.Many2many("pms.base.charge","pms_charge_line_base_rel","charge_id","base_id", "Base")

    _sql_constraints = [('name_uniq', 'unique (name)',
                         _("Name is exiting in the chrage applicable."))]

    @api.one
    def _compute_index(self):
        cr, uid, ctx = self.env.args
        self.index = self._model.search_count(cr,uid,[('sequence','<',self.sequence)],context=ctx) + 1

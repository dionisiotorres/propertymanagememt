from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PMSLeaseUnitChargeTypeLine(models.Model):
    _name = 'pms.lease.unit.charge.type.line'
    _description = "Lease Agreement Unit Charge Type"
    _inherit = ['mail.thread']

    applicable_charge_id = fields.Many2one("pms.applicable.charge.type",
                                           "Charge Name",
                                           required=True,
                                           track_visibility=True)
    charge_type_id = fields.Many2one(
        "pms.charge_types",
        related="applicable_charge_id.charge_type_id",
        required=True,
        readonly=True,
        track_visibility=True)
    calculation_method_id = fields.Many2one(
        'pms.calculation.method',
        "Calculation Method",
        related="applicable_charge_id.calculation_method_id",
        readonly=True)
    rate = fields.Float("Rate", store=True)
    total_amount = fields.Float("Total", compute="compute_total_amount")
    active = fields.Boolean(default=True)
    lease_line_id = fields.Many2one("pms.lease_agreement.line", "Lease Items")
    lease_id = fields.Many2one("pms.lease_agreement",
                               "Lease",
                               compute="get_lease_id")
    unit_no = fields.Many2one("pms.space.unit", "Unit", compute="get_lease_id")

    @api.one
    @api.depends('lease_line_id')
    def get_lease_id(self):
        if self.lease_line_id:
            self.lease_id = self.lease_line_id.lease_agreement_id.id
            self.unit_no = self.lease_line_id.unit_no.id

    @api.one
    @api.depends('charge_type_id', 'calculation_method_id', 'rate')
    def compute_total_amount(self):
        if self.calculation_method_id.name == 'Fix':
            self.total_amount = self.rate
        if self.calculation_method_id.name == 'Percentage':
            if self.lease_line_id:
                if not self.lease_line_id.pos_id:
                    raise UserError(_("Please set Pos ID in your Lease."))
                else:
                    pos_ids = self.env['pos.daily.sale'].search([
                        ('pos_interface_code', '=', 'POS-00001')
                    ])
                    pos_sale = 0
                    for l in pos_ids:
                        pos_sale += l.net_sales
                    amount = (pos_sale * self.rate) / 100
                    self.total_amount = amount
        if self.calculation_method_id.name == 'Area':
            if self.lease_line_id:
                area = self.lease_line_id.unit_no.area
                self.total_amount = (area * self.rate)
        if self.calculation_method_id.name == 'MeterUnit':
            if self.lease_line_id:
                amount = self.rate
                self.total_amount = amount * 170

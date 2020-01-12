from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PMSApplicableChargeLine(models.Model):
    _name = 'pms.application.charge.line'
    _description = "Applicable Charge Type Line"
    _inherit = ['mail.thread']

    application_id = fields.Many2one("pms.applicable.charge.type",
                                     "Charge Name",
                                     required=True,
                                     track_visibility=True)
    charge_type = fields.Many2one("pms.charge_types",
                                  related="application_id.charge_type",
                                  required=True,
                                  readonly=True,
                                  track_visibility=True)
    calculatedby = fields.Selection([('percent', 'Percentage'), ('fix', 'Fix'),
                                     ('area', 'Area'),
                                     ('meter_unit', 'Meter Unit')],
                                    "Calculated By",
                                    related="application_id.calculatedby",
                                    required=True,
                                    readonly=True,
                                    track_visibility=True)
    amount = fields.Float("Amount", store=True)
    total_amount = fields.Float("Total", compute="compute_total_amount")
    active = fields.Boolean(default=True)
    lease_line_id = fields.Many2one("pms.lease_agreement.line", "Lease Items")

    @api.one
    @api.depends('charge_type', 'calculatedby', 'amount')
    def compute_total_amount(self):
        if self.calculatedby == 'fix':
            self.total_amount = self.amount
        if self.calculatedby == 'percent':
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
                    amount = (pos_sale * self.amount) / 100
                    self.total_amount = amount
        if self.calculatedby == 'area':
            if self.lease_line_id:
                area = self.lease_line_id.unit_no.area
                self.total_amount = (area * self.amount)
        if self.calculatedby == 'meter_unit':
            if self.lease_line_id:
                amount = self.amount
                self.total_amount = amount * 170

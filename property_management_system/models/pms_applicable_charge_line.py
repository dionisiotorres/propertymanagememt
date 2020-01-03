from odoo import models, fields, api


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
    amount = fields.Float("Amount")
    total_amount = fields.Float("Total")
    active = fields.Boolean(default=True)
    lease_line_id = fields.Many2one("pms.lease_agreement.line", "Lease Items")

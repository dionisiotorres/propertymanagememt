from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    lease_no = fields.Char("Lease No", track_visibility=True)
    inv_month = fields.Char("Invoice Month",
                            readonly=True,
                            store=True,
                            track_visibility=True)
    property_id = fields.Many2one('pms.properties',
                                  "Properties",
                                  track_visibility=True)

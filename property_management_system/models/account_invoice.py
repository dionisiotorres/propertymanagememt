from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    lease_no = fields.Char("Lease No", track_visibility=True)
    lease_items = fields.Char("Lease Items", track_visibility=True)
    inv_month = fields.Char("Invoice Month",
                            readonly=True,
                            store=True,
                            track_visibility=True)
    property_id = fields.Many2one('pms.properties',
                                  "Properties",
                                  track_visibility=True)

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    charge_type_id = fields.Many2one("pms.applicable.charge.type","Charge Type")
    unit_no = fields.Many2one("pms.space.unit","Unit No")

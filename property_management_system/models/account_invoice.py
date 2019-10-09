from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    lease_no = fields.Char("Lease No")

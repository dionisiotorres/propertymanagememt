# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools


class utilitiesMonthly(models.Model):
    _name = "pms.utilities.monthly"
    _description = "Utiltiy Monthly"

    name = fields.Char("Shop")
    property_id = fields.Many2one("pms.properties", "Property")
    start_date = fields.Date("Bill SD")
    end_date = fields.Date("Bill ED")
    batch_code = fields.Char("Batch Code")
    billingperiod = fields.Char("Billing Period")
    transaction_type = fields.Char("Type")
    restapicode = fields.Char("RESTApiCode")
    utilities_no = fields.Char("Utilities No")
    end_value = fields.Float("End Value")
    start_value = fields.Float("Start Value")
    mobilemac_address = fields.Char("Mobile Mac Address")
    lastbillingvalue = fields.Float("Last Reading Value")
    utilities_type = fields.Char("utilities Type")
    status = fields.Selection([('unsubmit', "Umsubmit"), ('submit', 'Submit'),
                               ('confirm', 'Comfirm'), ('export', 'Export')],
                              "Status")
    extleaseno = fields.Many2one('pms.lease_agreement', "Ext Lease No")
    start_reading_date = fields.Date("LMR Date")
    end_reading_date = fields.Date("TMR Date")
    lastreadingnoh = fields.Float("Last Reading NOH")
    leasegreementitem_id = fields.Many2one("pms.lease_agreement.line",
                                           "Lease Agreement Item")
    lastbilling_date = fields.Date("Last Billing Date")
    use_value = fields.Float("Usage Value")

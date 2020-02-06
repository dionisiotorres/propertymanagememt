# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools


class utilitiesMonthly(models.Model):
    _name = "pms.utilities.monthly"
    _description = "Utiltiy Monthly"

    name = fields.Char("Shop")
    # property_id = fields.Many2one("pms.properties", "Property")
    property_code = fields.Char("PropertyCode")
    billingperiod = fields.Char("BillingPeriod")
    utilities_supply_type = fields.Char("UtilitiesSupplyType")
    utilities_source_type = fields.Char("UtilitiesSourceType")
    utilities_no = fields.Char("UtilitiesNo")
    end_value = fields.Float("End Value")
    start_value = fields.Float("Start Value")
    start_reading_date = fields.Date("LMR Date")
    end_reading_date = fields.Date("TMR Date")
    # start_date = fields.Date("Bill SD")
    # end_date = fields.Date("Bill ED")
    # batch_code = fields.Char("Batch Code")
    # restapicode = fields.Char("RESTApiCode")
    # mobilemac_address = fields.Char("Mobile Mac Address")
    # lastbillingvalue = fields.Float("Last Reading Value")
    # status = fields.Selection([('unsubmit', "Umsubmit"), ('submit', 'Submit'),
    #                            ('confirm', 'Comfirm'), ('export', 'Export')],
    #                           "Status")
    # extleaseno = fields.Many2one('pms.lease_agreement', "Ext Lease No")
    
    # lastreadingnoh = fields.Float("Last Reading NOH")
    # leasegreementitem_id = fields.Many2one("pms.lease_agreement.line",
    #                                        "Lease Agreement Item")
    # lastbilling_date = fields.Date("Last Billing Date")
    # use_value = fields.Float("Usage Value")

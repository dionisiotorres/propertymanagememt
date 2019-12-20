# # -*- coding: utf-8 -*-
# from odoo import api, fields, models

# class POSDailySale(models.Model):
#     _name = "pos.daily.sale"

#     property_id = fields.Many2one("pms.properties", "Mall", store=True)
#     batch_code = fields.Char("Batch Code")
#     tenant_code = fields.Char("Tenant Code")
#     busines_date = fields.Date("Business Date")
#     transaction_time = fields.Datetime("Transaction Time")
#     transaction_count = fields.Integer("Transaction Count")
#     currency = fields.Many2one("res.currency", "Currency")
#     grosssalesamount = fields.Float("Gross Sale Amount")
#     tax_amount = fields.Float("Tax")
#     servicecharge = fields.Float("Service Charge")
#     discount = fields.Float("Discount")
#     adjustment = fields.Float("Adjustment")
#     net_sale_amount = fields.Float("Net Sale Amount")
#     pos_interface_code = fields.Char("POS Interface Code")
#     pos_receipt_date = fields.Datetime("POS Receipt Date")
#     daily_sale_amtaftertax = fields.Float("DailySale AmountAfterTax")
#     daily_sale_amt_b4tax = fields.Float("DailySale AmountB4Tax")
#     daily_servicechargeamt = fields.Float("DailyService ChargeAmount")
#     daily_item_count = fields.Integer("Daily Item Count")
#     daily_receipt_count = fields.Integer("Daily Receipt Count")
#     ntd_flag = fields.Boolean("NTD Flag")
#     net_sales = fields.Float("Net Sales")
#     manual_net_sales = fields.Float("Manual Net Sales")

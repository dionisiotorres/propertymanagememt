# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, models


class POSDailySale(models.Model):
    _name = "pos.daily.sale"
    _description = 'POS Daily Sale'

    # property_id = fields.Many2one("pms.properties", "Mall", store=True)
    property_code = fields.Char("PropertyCode", store=True)
    pos_interface_code = fields.Char("POSInterfaceCode")
    pos_receipt_date = fields.Date("POSReceiptDate")
    grosssalesamount = fields.Float("GrossSaleAmount")
    currency = fields.Char("SaleCurrency")
    daily_sale_amt_b4tax = fields.Float("DailySaleAmtB4Tax")
    daily_servicechargeamt = fields.Float("DailyServiceChargeAmt")
    tax_amount = fields.Float("Tax")
    manual_net_sales = fields.Float("ManualNetSales")

    @api.multi
    def import_posdailysale(self):
        print(self)

    #     api_obj = self.env['pms.api.integration']
    #     data = []
    #     value = []
    #     apiinteg_id = api_obj.search([('name', '=', 'POSDailySaleT'),
    #                                   ('active', '=', True)])
    #     if apiinteg_id and apiinteg_id.property_id.api_integration == True:
    #         api_integ = apiinteg_id.generate_api_data({
    #             'id': apiinteg_id.id,
    #             'data': data
    #         })
    #         posdatas = []
    #         pos_sale_id = None
    #         daily_in_ids = self.search([])
    #         for datas in list(api_integ.items()):
    #             posdatas.append(datas[1])
    #         sale_id = posdatas[1]
    #         for sid in sale_id:
    #             currency_id = code = business_date = None
    #             code = self.env['pms.properties'].search([
    #                 ('code', '=', sid['propertyCode'])
    #             ]).code
    #             currency_id = self.env['res.currency'].search([
    #                 ('name', '=', sid['currency'])
    #             ]).id
    #             b_date = str(sid['businessDate'][0] + sid['businessDate'][1] +
    #                          sid['businessDate'][2] + sid['businessDate'][3]
    #                          ) + '-' + str(sid['businessDate'][4] +
    #                                        sid['businessDate'][5]) + '-' + str(
    #                                            sid['businessDate'][6] +
    #                                            sid['businessDate'][7])
    #             business_date = datetime.datetime.strptime(
    #                 b_date, '%Y-%m-%d').strftime('%Y-%m-%d')
    #             val = {
    #                 'property_id': code,
    #                 'tenant_code': sid['tenantCode'],
    #                 'busines_date': business_date,
    #                 # 'transaction_time': sid['transactionTime'],
    #                 'transaction_count': sid['transactionCount'],
    #                 'currency': currency_id,
    #                 'grosssalesamount': sid['grossSalesAmount'],
    #                 'tax_amount': sid['tax'],
    #                 'servicecharge': sid['serviceCharge'],
    #                 'discount': sid['discount'],
    #                 'adjustment': sid['adjustment'],
    #                 'net_sale_amount': sid['netSalesAmount'],
    #                 'pos_interface_code': sid['posInterfaceCode'],
    #                 # 'pos_receipt_date': sid['posReceiptDate'],
    #                 'daily_sale_amtaftertax': sid['dailySalesAmtAfterTax'],
    #                 'daily_sale_amt_b4tax': sid['dailySalesAmtB4Tax'],
    #                 'daily_servicechargeamt': sid['dailyServiceChargeAmt'],
    #                 'daily_item_count': sid['dailyItemCount'],
    #                 'daily_receipt_count': sid['dailyReceiptCount'],
    #                 'ntd_flag': sid['ntdFlag'],
    #                 'net_sales': sid['netSales'],
    #                 'manual_net_sales': sid['manualNetSales'],
    #             }
    #             pos_sale_id = super(POSDailySale, self).create(val)
    #         return pos_sale_id

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta


class PMSLeaseAgreement(models.Model):
    _name = 'pms.lease_agreement'
    _description = "Lease Agreements"

    name = fields.Char("Tanent", default="New", compute="compute_tanent")
    property_id = fields.Many2one("pms.properties")
    company_tanent_id = fields.Many2one("res.company",
                                        "Tanent",
                                        domain=[('company_type.name', '=',
                                                 "Tanent")])
    # tenant_type = fields.Char(related="company_tanent_id.company_type.name")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    extend_to = fields.Date("Extend Date")
    # old_end_date = fields.Date("OLED")
    vendor_type = fields.Char("Vendor Type")
    company_vendor_id = fields.Many2one('res.company',
                                        "Vendor",
                                        domain=[('company_type.name', '=',
                                                 "Vendor")])
    currency_id = fields.Many2one('res.currency', "Currency")
    pos_submission = fields.Boolean("Pos Submission")
    pos_submission_type = fields.Selection([('fpt', 'FTP'), ('ws', 'WS SOAP'),
                                            ('rap', 'Restful API'),
                                            ('manual', 'Manual')],
                                           "Submission Type",
                                           default='fpt')
    sale_data_type = fields.Selection([('TRAN', 'Transaction'),
                                       ('TRANW', 'Transaction /w Item'),
                                       ('DAILYSALE', 'Daily Sales'),
                                       ('MONTHLYSALE', 'Monthly Sales')],
                                      "Sales Data Type",
                                      default='TRAN')
    pos_submission_frequency = fields.Selection([('15MINUTE', '15 Minutes'),
                                                 ('DAILY', 'Daily'),
                                                 ('MONTHLY', 'Monthly')],
                                                "Submit Frequency",
                                                default='15MINUTE')
    reset_gp_flat = fields.Boolean("Reset GP Flag")
    reset_date = fields.Date("Reset Date")
    remark = fields.Text("Remark")
    state = fields.Selection([('BOOKING', 'Booking'), ('CONFIRM', 'Confirm'),
                              ('NEW', "New"), ('EXTENDED', "Extended"),
                              ('RENEWED', 'Renewed'),
                              ('CANCELLED', "Cancelled"),
                              ('TERMINATED', 'Terminated'),
                              ('EXPIRED', "Expired")],
                             string="Status",
                             default="BOOKING")
    active = fields.Boolean(default=True)
    lease_agreement_line = fields.One2many("pms.lease_agreement.line",
                                           "lease_agreement_id",
                                           "Lease Agreement Items")
    lease_no = fields.Char("Lease No", compute='get_lease_no')

    @api.multi
    @api.depends('property_id')
    def get_lease_no(self):
        if self.property_id:
            if self.property_id.property_management_id:
                for company in self.property_id.property_management_id:
                    if not company.lease_agre_format_id:
                        raise UserError(
                            _("Please set Your Lease Format in the property setting."
                              ))
                    if company.lease_agre_format_id and company.lease_agre_format_id.format_line_id:
                        for ft in company.lease_agre_format_id.format_line_id:
                            if ft.value_type == 'dynamic':
                                if self.property_id.code and ft.dynamic_value == 'property code':
                                    val.append(self.property_id.code)
                            if ft.value_type == 'fix':
                                val.append(ft.fix_value)
                            # if ft.value_type == 'digit':

                            if ft.value_type == 'datetime':
                                val.append(ft.datetime_value)
                        # space = []
                        # self.name = ''
                        # self.unit_code = ''
                        # if len(val) > 0:
                        #     for l in range(len(val)):
                        #         self.name += str(val[l])
                        #         self.unit_code += str(val[l])
                        #     if self.unit_no:
                        #         self.name += str(self.unit_no)

    @api.one
    @api.depends('company_tanent_id', 'lease_agreement_line')
    def compute_tanent(self):
        self.name = ''
        if self.company_tanent_id:
            self.name += self.company_tanent_id.name
        if self.lease_agreement_line:
            self.name += '('
            count = 1
            for lag in self.lease_agreement_line:
                for unit in lag.unit_no:
                    if lag and count < len(self.lease_agreement_line):
                        self.name += str(unit.name) + '|'
                    elif lag and count == len(self.lease_agreement_line):
                        self.name += str(unit.name) + ')'
                count += 1
            return self.name or 'New'

    @api.multi
    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.property_id:
            if self.property_id.property_management_id:
                for company in self.property_id.property_management_id:
                    if company.new_lease_term and company.new_lease_term.lease_period_type == 'month':
                        self.end_date = self.start_date + relativedelta(
                            months=company.new_lease_term.min_time_period)
                    elif company.new_lease_term and company.new_lease_term.lease_period_type == 'year':
                        self.end_date = self.start_date + relativedelta(
                            years=company.new_lease_term.min_time_period)

    @api.multi
    def toggle_active(self):
        for la in self:
            if not la.active:
                la.active = self.active
        super(PMSLeaseAgreement, self).toggle_active()

    @api.multi
    def action_confirm(self):
        return self.write({'state': 'CONFIRM'})

    @api.multi
    def action_activate(self):
        return self.write({'state': 'NEW'})

    @api.multi
    def action_cancel(self):
        return self.write({'state': 'CANCELLED'})

    @api.multi
    def action_reset_confirm(self):
        return self.write({'state': 'CONFIRM'})

    @api.multi
    def action_extend(self):
        return self.write({'state': 'EXTENDED'})

    @api.multi
    def action_renew(self):
        return self.write({'state': 'RENEWED'})

    @api.multi
    def action_terminate(self):
        return self.write({'state': 'TERMINATED'})


class PMSLeaseAgreementLine(models.Model):
    _name = 'pms.lease_agreement.line'
    _description = "Lease Agreement Line"

    lease_agreement_id = fields.Many2one("pms.lease_agreement",
                                         "Lease Agreement")

    unit_no = fields.Many2one("pms.space.unit")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    extend_to = fields.Date("Extend Date")
    company_tanent_id = fields.Many2one(
        'res.company',
        "Shop",
    )
    pos_id = fields.Char("POS ID")
    remark = fields.Text("Remark")
    rental_charge_type = fields.Selection([('base', 'Base'),
                                           ('base+gto', 'Base + GTO'),
                                           ('baseorgto', 'Base or GTO')],
                                          string="Rental Charge Type")


class PMSChargeType(models.Model):
    _name = 'pms.charge_type'
    _description = "Charge Types"

    name = fields.Char("Description", required=True)
    code = fields.Char("Code", required=True)
    active = fields.Boolean(default=True)
    _sql_constraints = [
        ('name_code_unique', 'unique(code)',
         'Please add other CODE that is exiting in the database.')
    ]

    @api.multi
    def toggle_active(self):
        for la in self:
            if not la.active:
                la.active = self.active
        super(PMSChargeType, self).toggle_active()


class PMSChargeFormula(models.Model):
    _name = 'pms.charge.formula'
    _description = "Charge Formulas"

    name = fields.Char("Description", required=True)
    code = fields.Char("Code", required=True)
    active = fields.Boolean(default=True)
    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'Please add other CODE that is exiting in the database.')
    ]

    @api.multi
    def toggle_active(self):
        for la in self:
            if not la.active:
                la.active = self.active
        super(PMSChargeFormula, self).toggle_active()


class PMSTradeCategory(models.Model):
    _name = "pms.trade_category"
    _description = "Trade Category"

    name = fields.Char("Descritpion", required=True)
    code = fields.Char("Code", required=True)
    active = fields.Boolean(default=True)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.name
            result.append((record.id, code))
        return result


class PMSSubTradeCategory(models.Model):
    _name = "pms.sub_trade_category"
    _description = "Sub Trade Category"

    name = fields.Char("Description", required=True)
    code = fields.Char("Code", required=True)
    trade_id = fields.Many2one("pms.trade_category", "Trade")
    active = fields.Boolean(default=True)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.name
            result.append((record.id, code))
        return result
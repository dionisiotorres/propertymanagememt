from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta


class PMSLeaseAgreement(models.Model):
    _name = 'pms.lease_agreement'
    _description = "Lease Agreements"

    name = fields.Char("Name", default="New", compute="compute_tanent")
    property_id = fields.Many2one("pms.properties")
    company_tanent_id = fields.Many2one("res.company",
                                        "Tanent",
                                        domain=[('company_type.name', '=',
                                                 "Tanent")])
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    extend_to = fields.Date("Extend Date")
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
    state = fields.Selection([('BOOKING', 'Booking'), ('NEW', "New"),
                              ('EXTENDED', "Extended"), ('RENEWED', 'Renewed'),
                              ('CANCELLED', "Cancelled"),
                              ('TERMINATED', 'Terminated'),
                              ('EXPIRED', "Expired")],
                             string="Status",
                             default="BOOKING")
    active = fields.Boolean(default=True)
    lease_agreement_line = fields.One2many("pms.lease_agreement.line",
                                           "lease_agreement_id",
                                           "Lease Agreement Items")
    lease_no = fields.Char("Lease No", default="New", store=True)
    company_id = fields.Many2one(
        'res.company',
        "Company",
        default=lambda self: self.env.user.company_id.id)

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

    # @api.multi
    # def action_confirm(self):
    #     return self.write({'state': 'CONFIRM'})

    @api.multi
    def action_activate(self):
        if self.lease_agreement_line:
            for line in self.lease_agreement_line:
                for unit in line.unit_no:
                    unit.write({'status': 'occupied'})
                if self.company_id.rentschedule_type == 'probation':
                    date = None
                    start_date = None
                    end_date = None
                    day = 1
                    while day >= 1:
                        if not end_date:
                            end_date = line.start_date
                        if line.end_date > end_date:
                            if not start_date:
                                start_date = line.start_date
                            if start_date == line.start_date:
                                date = start_date
                                end_date = start_date + relativedelta(months=1)
                                start_date = start_date + relativedelta(
                                    months=1)
                                val = {
                                    'property_id': self.property_id.id,
                                    'lease_agreement_line_id': line.id,
                                    'charge_type': line.rental_charge_type,
                                    'amount': line.rent,
                                    'start_date': date,
                                    'end_date': end_date,
                                }
                                self.env['pms.rent_schedule'].create(val)
                                day = 1
                            else:
                                start_date = end_date
                                end_date = start_date + relativedelta(months=1)
                                day = 1
                                val = {
                                    'property_id': self.property_id.id,
                                    'lease_agreement_line_id': line.id,
                                    'charge_type': line.rental_charge_type,
                                    'amount': line.rent,
                                    'start_date': start_date,
                                    'end_date': end_date,
                                }
                                self.env['pms.rent_schedule'].create(val)
                        else:
                            day = 0
        return self.write({'state': 'NEW'})

    @api.multi
    def action_cancel(self):
        return self.write({'state': 'CANCELLED'})

    @api.multi
    def action_reset_confirm(self):
        return self.write({'state': 'BOOKING'})

    @api.multi
    def action_extend(self):
        if not self.company_id.extend_lease_term:
            raise UserError(
                _("Please set extend term in the property setting."))
        else:
            self.extend_to = self.end_date + relativedelta(
                months=self.company_id.extend_lease_term.min_time_period)
        return self.write({'state': 'EXTENDED'})

    @api.multi
    def action_renew(self):
        return self.write({'state': 'RENEWED'})

    @api.multi
    def action_terminate(self):
        if not self.company_id.extend_lease_term:
            raise UserError(
                _("Please set extend term in the property setting."))
        # else:
        #     self.extend_to = self.end_date + relativedelta(
        #         months=self.company_id.extend_lease_term.min_time_period)
        return self.write({'state': 'TERMINATED'})

    @api.model
    def create(self, values):
        if values['property_id']:
            property_id = self.env['pms.properties'].browse(
                values['property_id'])
            if property_id.property_management_id:
                for company in property_id.property_management_id:
                    if not company.lease_agre_format_id:
                        raise UserError(
                            _("Please set Your Lease Format in the property setting."
                              ))
                    if company.lease_agre_format_id and company.lease_agre_format_id.format_line_id:
                        val = []
                        for ft in company.lease_agre_format_id.format_line_id:
                            if ft.value_type == 'dynamic':
                                if property_id.code and ft.dynamic_value == 'property code':
                                    val.append(property_id.code)
                            if ft.value_type == 'fix':
                                val.append(ft.fix_value)
                            if ft.value_type == 'digit':
                                sequent_ids = self.env['ir.sequence'].search([
                                    ('name', '=', 'Lease Agreement')
                                ])
                                sequent_ids.padding = ft.digit_value
                            if ft.value_type == 'datetime':
                                mon = yrs = ''
                                if ft.datetime_value == 'MM':
                                    mon = datetime.today().month
                                    val.append(mon)
                                if ft.datetime_value == 'MMM':
                                    mon = datetime.today().strftime('%b')
                                    val.append(mon)
                                if ft.datetime_value == 'YY':
                                    yrs = datetime.today().strftime("%y")
                                    val.append(yrs)
                                if ft.datetime_value == 'YYYY':
                                    yrs = datetime.today().strftime("%Y")
                                    val.append(yrs)
                        space = []
                        lease_no_pre = ''
                        if len(val) > 0:
                            for l in range(len(val)):
                                lease_no_pre += str(val[l])
        lease_no = ''
        lease_no += self.env['ir.sequence'].with_context(
            force_company=values['company_id']).next_by_code(
                'pms.lease_agreement')
        values['lease_no'] = lease_no_pre + lease_no
        return super(PMSLeaseAgreement, self).create(values)


class PMSLeaseAgreementLine(models.Model):
    _name = 'pms.lease_agreement.line'
    _description = "Lease Agreement Line"

    lease_agreement_id = fields.Many2one("pms.lease_agreement",
                                         "Lease Agreement")
    unit_no = fields.Many2one("pms.space.unit",
                              domain=[('status', 'in', ['vacant']),
                                      ('unittype_id.chargeable', '=', True)])
    start_date = fields.Date(string="Start Date",
                             related="lease_agreement_id.start_date")
    end_date = fields.Date(string="End Date",
                           related="lease_agreement_id.end_date")
    extend_to = fields.Date("Extend Date")
    rent = fields.Float(string="Rent", related="unit_no.rate")
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
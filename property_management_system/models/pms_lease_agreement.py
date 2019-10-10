import datetime
import calendar
from calendar import monthrange
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class PMSLeaseAgreement(models.Model):
    _name = 'pms.lease_agreement'
    _description = "Lease Agreements"

    name = fields.Char("Name", default="New", compute="compute_tanent")
    property_id = fields.Many2one("pms.properties")
    company_tanent_id = fields.Many2one("res.company",
                                        "Tenant",
                                        domain=[('company_type.name', '=',
                                                 "Tenant")])
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
    old_lease_no = fields.Char("Old Lease No", default="", store=True)
    extend_count = fields.Float("Extend Count", store=True)
    is_terminate = fields.Boolean("Is Terminate")
    terminate_period = fields.Date("Terminate Date")
    unit_no = fields.Char("Unit", default='', compute="compute_tanent")
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
            self.unit_no = ''
            self.name += '('
            count = 1
            for lag in self.lease_agreement_line:
                for unit in lag.unit_no:
                    if lag and count < len(self.lease_agreement_line):
                        self.name += str(unit.name) + '|'
                        self.unit_no += str(unit.name) + '|'
                    elif lag and count == len(self.lease_agreement_line):
                        self.name += str(unit.name) + ')'
                        self.unit_no += str(unit.name)
                count += 1
            # return self.name or 'New'

    @api.multi
    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.property_id:
            if self.property_id.property_management_id:
                for company in self.property_id.property_management_id:
                    if company.new_lease_term and company.new_lease_term.lease_period_type == 'month':
                        self.end_date = self.start_date + relativedelta(
                            months=company.new_lease_term.min_time_period) - relativedelta(days=1)
                    elif company.new_lease_term and company.new_lease_term.lease_period_type == 'year':
                        self.end_date=self.start_date+relativedelta(years=company.new_lease_term.min_time_period)-relativedelta(days=1)
            else:
                raise UserError(_("Pease set management company with your mall."))

    @api.multi
    def toggle_active(self):
        for la in self:
            if not la.active:
                la.active = self.active
        super(PMSLeaseAgreement, self).toggle_active()

    # @api.multi
    # def action_view_invoice(self):
    #     invoices = self.env['account.invoice'].search([('lease_no', '=', self.lease_no)])
    #     action = self.env.ref('account.action_invoice_tree1').read()[0]
    #     if len(invoices) > 1:
    #         action['domain'] = [('id', 'in', invoices.ids)]
    #     elif len(invoices) == 1:
    #         action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
    #         action['res_id'] = invoices.ids[0]
    #     else:
    #         action = {'type': 'ir.actions.act_window_close'}
    #     return action

    # @api.multi
    # def action_invoice(self):
    #     invoices = self.env['account.invoice'].search([('lease_no', '=', self.lease_no)])
    #     if not invoices:
    #         payment_term = self.env['account.payment.term'].search([('name', '=', 'Immediate Payment')])
    #         invoice_lines = []
    #         for l in self.lease_agreement_line:
    #             val = {
    #                 'name': l.unit_no.name,
    #             }
    #             product_tmp_id = self.env['product.template'].create(val)
    #             product_id = self.env['product.product'].create({'product_tmpl_id': product_tmp_id.id})
    #             account_id = False
    #             if product_id.id:
    #                 account_id = product_id.property_account_income_id.id or product_id.categ_id.property_account_income_categ_id.id
    #             taxes = product_id.taxes_id.filtered(lambda r: not self.company_id or r.company_id == self.company_id)
    #             value = {
    #                 'name': _('Payment'),
    #                 'account_id': account_id,
    #                 'price_unit': l.rent,
    #                 'quantity': l.unit_no.area,
    #                 'uom_id': l.unit_no.uom.id,
    #                 'product_id': product_id.id,
    #                 'sale_line_ids': [(6, 0, [l.id])],
    #                 'invoice_line_tax_ids': [(6, 0, taxes.ids)],
    #             }
    #             inv_line_id = self.env['account.invoice.line'].create(value)
    #             invoice_lines.append(inv_line_id.id)
    #         invoices = self.env['account.invoice'].create({
    #             'lease_no': self.lease_no,
    #             'partner_id': self.company_tanent_id.id,
    #             'company_id': self.company_id.id,
    #             'payment_term_id': payment_term.id,
    #             'invoice_line_ids': [(6, 0, invoice_lines)],
    #             })
    #     if invoices:
    #         return self.action_view_invoice()
    #     return {'type': 'ir.actions.act_window_close'}

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
                        if line.start_date and line.end_date:
                            if not end_date:
                                end_date = line.start_date
                            if line.end_date > end_date:
                                if not start_date:
                                    start_date = line.start_date
                                if start_date == line.start_date:
                                    date = start_date
                                    end_date = start_date + relativedelta(
                                        months=1)
                                    start_date = start_date + relativedelta(
                                        months=1)
                                    val = {
                                        'property_id': self.property_id.id,
                                        'lease_agreement_line_id': line.id,
                                        'charge_type': line.rental_charge_type,
                                        'amount': line.rent,
                                        'start_date': date,
                                        'end_date': end_date + relativedelta(
                                        days=1),
                                    }
                                    self.env['pms.rent_schedule'].create(val)
                                    day = 1
                                else:
                                    start_date = end_date
                                    end_date = start_date + relativedelta(
                                        months=1)
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
                        else:
                            raise UserError(
                                _("Please set start date and end date for your lease."
                                  ))
                if self.company_id.rentschedule_type == 'calendar':
                    date = None
                    start_date = None
                    end_date = None
                    s_day = 0
                    last_day = 0
                    day = 1
                    first_month_day = 0
                    while day >= 1:
                        if line.start_date and line.end_date:
                            s_day = line.start_date.day
                            last_day = calendar.monthrange(line.start_date.year, line.start_date.month)[1]     
                            if not end_date:
                                end_date = line.start_date
                            if line.end_date > end_date:
                                if not start_date:
                                    start_date = line.start_date
                                if start_date == line.start_date:
                                    date = start_date
                                    end_date = start_date + relativedelta(
                                        days=last_day - s_day)
                                    start_date = start_date + relativedelta(days=(last_day - s_day) + 1)
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
                                    start_date = end_date + relativedelta(days = 1)
                                    l_day = calendar.monthrange(start_date.year, start_date.month)[1]
                                    end_date = end_date + relativedelta(days = l_day)
                                    if end_date >= line.end_date:
                                        end_date = line.end_date
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
                        else:
                            raise UserError(
                                _("Please set start date and end date for your lease."
                                  ))
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
            self.extend_count += 1
            if self.extend_count > self.company_id.extend_count:
                raise UserError(_("Extend Limit is Over."))
            if self.extend_to:
                self.extend_to = self.extend_to + relativedelta(
                    months=self.company_id.extend_lease_term.min_time_period)
            else:
                self.extend_to = self.end_date + relativedelta(
                    months=self.company_id.extend_lease_term.min_time_period)
        return self.write({'state': 'EXTENDED'})

    @api.multi
    def action_renew(self):
        line = []
        if self.lease_agreement_line:
            for l in self.lease_agreement_line:
                lease_line_id = self.env['pms.lease_agreement.line'].search([
                    ('id', '=', l.id)
                ])
                for les in lease_line_id:
                    value = {
                        'unit_no': les.unit_no.id,
                        'start_date': les.end_date,
                        'rent': les.rent,
                        'company_tanent_id': les.company_tanent_id.id,
                        'pos_id': les.pos_id,
                        'remark': les.remark,
                        'rental_charge_type': les.rental_charge_type,
                    }
                    line_id = self.env['pms.lease_agreement.line'].create(
                        value).id
                line.append(line_id)
        val = {
            'name': self.name,
            'property_id': self.property_id.id,
            'company_tanent_id': self.company_tanent_id.id,
            'start_date': self.end_date,
            'vendor_type': self.vendor_type,
            'company_vendor_id': self.company_vendor_id.id,
            'currency_id': self.currency_id.id,
            'pos_submission': self.pos_submission,
            'pos_submission_type': self.pos_submission_type,
            'sale_data_type': self.sale_data_type,
            'pos_submission_frequency': self.pos_submission_frequency,
            'reset_gp_flat': self.reset_gp_flat,
            'reset_date': self.reset_date,
            'remark': self.remark,
            'state': 'BOOKING',
            'active': self.active,
            'lease_agreement_line': [(6, 0, line)],
            'lease_no': self.lease_no,
            'old_lease_no': self.lease_no,
            'company_id': self.company_id.id,
        }
        new_lease_ids = self.env['pms.lease_agreement'].create(val)
        self.write({'state': 'RENEWED'})
        return new_lease_ids.action_view_new_lease()

    @api.multi
    @api.onchange('is_terminate')
    def onchange_is_terminate(self):
        if self.is_terminate == True:
            if not self.company_id.pre_notice_terminate_term:
                raise UserError(
                    _("Please set terminate term in the property setting."))
            else:
                self.is_terminate = True
                self.terminate_period = (datetime.today() + relativedelta(
                    days=self.company_id.pre_notice_terminate_term)
                                         ).strftime('%Y-%m-%d')

    @api.multi
    def action_terminate(self):
        if self.is_terminate == True and self.terminate_period:
            if self.terminate_period <= datetime.now().date():
                return self.write({'state': 'TERMINATED'})
            else:
                raise UserError(
                    _("Today date (%s) must be greater than or equal Tarminate date (%s)"
                      % (datetime.now().date(), self.terminate_period)))
        else:
            raise UserError(
                _("Please click is Terminate to set terminate date."))
        return self.write({'state': 'TERMINATED'})

    @api.multi
    def action_view_new_lease(self):
        leases = self.env['pms.lease_agreement'].search([('old_lease_no', '=',
                                                          self.lease_no)])
        action = self.env.ref(
            'property_management_system.action_lease_aggrement_all').read()[0]
        if leases:
            action['views'] = [(self.env.ref(
                'property_management_system.view_lease_aggrement_form').id,
                                'form')]
            action['res_id'] = leases.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

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

    def get_start_date(self):
        if self._context.get('start_date') != False:
            return self._context.get('start_date')

    def get_end_date(self):
        if self._context.get('end_date') != False:
            return self._context.get('end_date')

    name = fields.Char("Name", compute="compute_name")
    lease_agreement_id = fields.Many2one("pms.lease_agreement",
                                         "Lease Agreement")
    lease_no = fields.Char("Lease No", related="lease_agreement_id.lease_no", store=True)
    unit_no = fields.Many2one("pms.space.unit",
                              domain=[('status', 'in', ['vacant']),
                                      ('unittype_id.chargeable', '=', True)])
    start_date = fields.Date(string="Start Date", default=get_start_date, readonly=False, store=True)
    end_date = fields.Date(string="End Date",default=get_end_date, readonly=False,  store=True)
    extend_to = fields.Date("Extend Date")
    rent = fields.Float(string="Rent", related="unit_no.rate", store=True)
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

    rent_schedule_line = fields.One2many('pms.rent_schedule', 'lease_agreement_line_id', "Rent Schedules")
    rent_total = fields.Float("Amount(per month)", compute="get_total_rent", store=True, readonly=False)
    area = fields.Integer("Area", related="unit_no.area")
    gto_percentage = fields.Integer("GTO Percent(%)")
    maintain_charge = fields.Float("Maintain Charge", store=True, readonly=False)
    state = fields.Selection([('BOOKING', 'Booking'), ('NEW', "New"),
                              ('EXTENDED', "Extended"), ('RENEWED', 'Renewed'),
                              ('CANCELLED', "Cancelled"),
                              ('TERMINATED', 'Terminated'),
                              ('EXPIRED', "Expired")],
                             string="Status",
                             related="lease_agreement_id.state", store=True)

    @api.one
    @api.depends('unit_no', 'lease_no')
    def compute_name(self):
        self.name = ''
        if self.unit_no and self.lease_no:
            self.name = self.lease_no + '/' + self.unit_no.name
        elif self.lease_no and not self.unit_no:
            self.name = self.lease_no
        elif self.unit_no and not self.lease_no:
            self.name = self.unit_no.name
        else:
            self.name = 'New'

    @api.one
    @api.depends('rent', 'area')
    def get_total_rent(self):
        total = 0
        total = self.area * self.rent
        self.rent_total = total
    
    @api.multi
    def action_view_invoice(self):
        invoices = self.env['account.invoice'].search([('lease_no', '=', self.lease_no)])
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_invoice(self):
        invoices = self.env['account.invoice'].search([('lease_no', '=', self.lease_no)])
        if not invoices:
            payment_term = self.env['account.payment.term'].search([('name', '=', 'Immediate Payment')])
            invoice_lines = []
            for l in self.rent_schedule_line:
                val = {
                    'name': l.lease_agreement_line_id.name,
                }
                product_tmp_id = self.env['product.template'].create(val)
                product_id = self.env['product.product'].create({'product_tmpl_id': product_tmp_id.id})
                account_id = False
                if product_id.id:
                    account_id = product_id.property_account_income_id.id or product_id.categ_id.property_account_income_categ_id.id
                taxes = product_id.taxes_id.filtered(lambda r: not self.lease_agreement_id.company_id or r.company_id == self.lease_agreement_id.company_id)
                value = {
                    'name': _('Payment'),
                    'account_id': account_id,
                    'price_unit': self.rent,
                    'quantity': self.area,
                    'uom_id': self.unit_no.uom.id,
                    'product_id': product_id.id,
                    'sale_line_ids': [(6, 0, [l.id])],
                    'invoice_line_tax_ids': [(6, 0, taxes.ids)],
                }
                inv_line_id = self.env['account.invoice.line'].create(value)
                invoice_lines.append(inv_line_id.id)
            invoices = self.env['account.invoice'].create({
                'lease_no': self.lease_no,
                'partner_id': self.lease_agreement_id.company_tanent_id.id,
                'company_id': self.lease_agreement_id.company_id.id,
                'payment_term_id': payment_term.id,
                'invoice_line_ids': [(6, 0, invoice_lines)],
                })
        if invoices:
            return self.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

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

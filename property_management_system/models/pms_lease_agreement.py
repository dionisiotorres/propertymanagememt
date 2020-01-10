import datetime
import calendar
from calendar import monthrange
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class PMSLeaseAgreement(models.Model):
    _name = 'pms.lease_agreement'
    _inherit = ['mail.thread']
    _description = "Lease Agreements"
    _order = "property_id, company_tanent_id, state, start_date"

    name = fields.Char("Name", default="New", compute="compute_tanent", track_visibility=True)
    property_id = fields.Many2one("pms.properties", track_visibility=True)
    company_tanent_id = fields.Many2one("res.partner",
                                        "Tenant", track_visibility=True,
                                        domain=[('company_channel_type.name', '=',
                                                 "Tenant")])
    start_date = fields.Date("Start Date", track_visibility=True)
    end_date = fields.Date("End Date", track_visibility=True)
    extend_to = fields.Date("Extend End", track_visibility=True)
    vendor_type = fields.Char("Vendor Type", track_visibility=True)
    company_vendor_id = fields.Many2one('res.partner',
                                        "Vendor", track_visibility=True,
                                        domain=[('company_channel_type.name', '=',
                                                 "Vendor")])
    currency_id = fields.Many2one('res.currency', "Currency", related="property_id.currency_id", track_visibility=True)
    pos_submission = fields.Boolean("Pos Submission", track_visibility=True)
    pos_submission_type = fields.Selection([('fpt', 'FTP'), ('ws', 'WS SOAP'),
                                            ('rap', 'Restful API'),
                                            ('manual', 'Manual')],
                                           "Submission Type",
                                           default='fpt', track_visibility=True)
    sale_data_type = fields.Selection([('TRAN', 'Transaction'),
                                       ('TRANW', 'Transaction /w Item'),
                                       ('DAILYSALE', 'Daily Sales'),
                                       ('MONTHLYSALE', 'Monthly Sales')],
                                      "Sales Data Type",
                                      default='TRAN', track_visibility=True)
    pos_submission_frequency = fields.Selection([('15MINUTE', '15 Minutes'),
                                                 ('DAILY', 'Daily'),
                                                 ('MONTHLY', 'Monthly')],
                                                "Submit Frequency",
                                                default='15MINUTE', track_visibility=True)
    reset_gp_flat = fields.Boolean("Reset GP Flag", track_visibility=True)
    reset_date = fields.Date("Reset Date", track_visibility=True)
    remark = fields.Text("Remark", track_visibility=True)
    state = fields.Selection([('BOOKING', 'Booking'), ('NEW', "New"),
                              ('EXTENDED', "Extended"), ('RENEWED', 'Renewed'),
                              ('CANCELLED', "Cancelled"),
                              ('TERMINATED', 'Terminated'),
                              ('EXPIRED', "Expired")],
                             string="Status",
                             default="BOOKING", track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)
    lease_agreement_line = fields.One2many("pms.lease_agreement.line",
                                           "lease_agreement_id",
                                           "Lease Agreement Items", track_visibility=True)
    lease_no = fields.Char("Lease No", default="New", store=True, track_visibility=True)
    old_lease_no = fields.Char("Old Lease No", default="", store=True, track_visibility=True)
    extend_count = fields.Integer("Extend Times", store=True, track_visibility=True)
    is_terminate = fields.Boolean("Is Terminate", track_visibility=True)
    terminate_period = fields.Date("Terminate Date", track_visibility=True)
    unit_no = fields.Char("Unit", default='', compute="compute_tanent", store =True, track_visibility=True)
    company_id = fields.Many2one(
        'res.company',
        "Company",
        default=lambda self: self.env.user.company_id.id, track_visibility=True)
    lease_rent_config_id = fields.One2many("pms.rent_schedule", "lease_agreement_id", "Rental Details", track_visibility=True)

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
            self.end_date = company = None
            company = self.property_id
            if not company.new_lease_term:
                raise UserError(_("Please set new lease term in Property."))
            if company.new_lease_term and company.new_lease_term.lease_period_type == 'month':
                self.end_date = self.start_date + relativedelta(
                    months=company.new_lease_term.min_time_period) - relativedelta(days=1)
            if company.new_lease_term and company.new_lease_term.lease_period_type == 'year':
                self.end_date = self.start_date+relativedelta(years=company.new_lease_term.min_time_period)-relativedelta(days=1)              

    @api.multi
    def toggle_active(self):
        for la in self:
            if not la.active:
                la.active = self.active
        super(PMSLeaseAgreement, self).toggle_active()

    @api.multi
    def action_activate(self):
        if self.lease_agreement_line:
            for line in self.lease_agreement_line:
                for unit in line.unit_no:
                    unit.write({'status': 'occupied'})
                for ctype in line.appilication_type:
                    if self.property_id.rentschedule_type == 'prorated':
                        date = None
                        start_date = None
                        end_date = None
                        day = 1
                        while day >= 1:
                            if line.start_date and line.end_date:
                                if not end_date:
                                    if line.state == 'NEW':
                                        end_date = line.end_date
                                    elif line.state == 'EXTENDED':
                                        end_date = line.extend_start
                                    else:
                                        end_date = line.start_date
                                if line.end_date > end_date:
                                    if not start_date:
                                        start_date = line.start_date
                                    if start_date == line.start_date:
                                        date = start_date
                                        end_date = start_date + relativedelta(
                                            months=1)
                                        end_date = end_date - relativedelta(
                                            days=1)
                                        start_date = date + relativedelta(
                                            months=1)
                                        val = {
                                            'property_id': self.property_id.id,
                                            'lease_agreement_line_id': line.id,
                                            'lease_agreement_id': self.id,
                                            'charge_type': ctype.application_id.id,
                                            'amount': ctype.total_amount,
                                            'start_date': date,
                                            'end_date': end_date,
                                            'extend_count': line.extend_count,
                                            'extend_to': line.extend_to,
                                        }
                                        self.env['pms.rent_schedule'].create(val)
                                        day = 1
                                    else:
                                        start_date = end_date + relativedelta(days=1)
                                        end_date = start_date + relativedelta(
                                            months=1)
                                        end_date = end_date - relativedelta(days=1)
                                        end_date
                                        day = 1
                                        val = {
                                            'property_id': self.property_id.id,
                                            'lease_agreement_line_id': line.id,
                                            'lease_agreement_id': self.id,
                                            'charge_type': ctype.application_id.id,
                                            'amount': ctype.total_amount,
                                            'start_date': start_date,
                                            'end_date': end_date,
                                            'extend_count': line.extend_count,
                                            'extend_to': line.extend_to,
                                        }
                                        self.env['pms.rent_schedule'].create(val)
                                elif line.state == 'NEW' and line.end_date <= end_date and line.extend_to >= end_date + relativedelta(days=2):
                                    if not start_date:
                                        start_date = line.end_date
                                    if start_date == line.end_date:
                                        date = start_date
                                        end_date = start_date + relativedelta(
                                            months=1)
                                        end_date = end_date - relativedelta(
                                            days=1)
                                        start_date = date + relativedelta(
                                            months=1)
                                        val = {
                                            'property_id': self.property_id.id,
                                            'lease_agreement_line_id': line.id,
                                            'lease_agreement_id': self.id,
                                            'charge_type': ctype.application_id.id,
                                            'amount': ctype.total_amount,
                                            'start_date': date,
                                            'end_date': end_date,
                                            'extend_count': line.extend_count,
                                            'extend_to': line.extend_to,
                                        }
                                        self.env['pms.rent_schedule'].create(val)
                                        day = 1
                                    else:
                                        start_date = end_date + relativedelta(days=1)
                                        end_date = start_date + relativedelta(
                                            months=1)
                                        end_date = end_date - relativedelta(days=1)
                                        end_date
                                        day = 1
                                        val = {
                                            'property_id': self.property_id.id,
                                            'lease_agreement_line_id': line.id,
                                            'lease_agreement_id': self.id,
                                            'charge_type': ctype.application_id.id,
                                            'amount': ctype.total_amount,
                                            'start_date': start_date,
                                            'end_date': end_date,
                                            'extend_count': line.extend_count,
                                            'extend_to': line.extend_to,
                                        }
                                        self.env['pms.rent_schedule'].create(val)
                                elif line.state == 'EXTENDED' and line.extend_to >= end_date + relativedelta(
                                            days=2):
                                    if not start_date:
                                        start_date = line.extend_start
                                    if start_date == line.extend_start:
                                        date = start_date
                                        end_date = start_date + relativedelta(
                                            months=1)
                                        end_date = end_date - relativedelta(
                                            days=1)
                                        start_date = date + relativedelta(
                                            months=1)
                                        val = {
                                            'property_id': self.property_id.id,
                                            'lease_agreement_line_id': line.id,
                                            'lease_agreement_id': self.id,
                                            'charge_type': ctype.application_id.id,
                                            'amount': ctype.total_amount,
                                            'start_date': date,
                                            'end_date': end_date,
                                            'extend_count': line.extend_count,
                                            'extend_to': line.extend_to,
                                        }
                                        self.env['pms.rent_schedule'].create(val)
                                        day = 1
                                    else:
                                        start_date = end_date + relativedelta(days=1)
                                        end_date = start_date + relativedelta(
                                            months=1)
                                        end_date = end_date - relativedelta(days=1)
                                        end_date
                                        day = 1
                                        val = {
                                            'property_id': self.property_id.id,
                                            'lease_agreement_line_id': line.id,
                                            'lease_agreement_id': self.id,
                                            'charge_type': ctype.application_id.id,
                                            'amount': ctype.total_amount,
                                            'start_date': start_date,
                                            'end_date': end_date,
                                            'extend_count': line.extend_count,
                                            'extend_to': line.extend_to,
                                        }
                                        self.env['pms.rent_schedule'].create(val)
                                else:
                                    day = 0
                            else:
                                raise UserError(
                                    _("Please set start date and end date for your lease."
                                    ))
                    if self.property_id.rentschedule_type == 'calendar':
                        date = None
                        start_date = None
                        end_date = None
                        s_day = 0
                        last_day = 0
                        day = 1
                        first_month_day = 0
                        while day >= 1:
                            if line.start_date and line.end_date:
                                if not end_date:
                                    if line.state == 'NEW':
                                        end_date = line.end_date
                                    elif line.state == 'EXTENDED':
                                        end_date = line.extend_start
                                    else:
                                        end_date = line.start_date
                                if line.end_date > end_date:
                                    s_day = line.start_date.day
                                    last_day = calendar.monthrange(line.start_date.year, line.start_date.month)[1]
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
                                            'lease_agreement_id': self.id,
                                            'charge_type': ctype.application_id.id,
                                            'amount': ctype.total_amount,
                                            'start_date': date,
                                            'end_date': end_date,
                                            'extend_count': line.extend_count,
                                            'extend_to': line.extend_to,
                                        }
                                        self.env['pms.rent_schedule'].create(val)
                                        day = 1
                                    else:
                                        start_date = end_date + relativedelta(days = 1)
                                        l_day = calendar.monthrange(start_date.year, start_date.month)[1]
                                        end_date = end_date + relativedelta(days = l_day)
                                        if self.state == 'BOOKING' and end_date > line.end_date:
                                            end_date = line.end_date
                                        if self.state == 'NEW' and end_date > line.extend_to:
                                            end_date = line.extend_to
                                        if self.state == 'EXTENDED' and end_date > line.extend_to:
                                            end_date = line.extend_to
                                        
                                        day = 1
                                        val = {
                                            'property_id': self.property_id.id,
                                            'lease_agreement_line_id': line.id,
                                            'lease_agreement_id': self.id,
                                            'charge_type': ctype.application_id.id,
                                            'amount': ctype.total_amount,
                                            'start_date': start_date,
                                            'end_date': end_date,
                                            'extend_count': line.extend_count,
                                            'extend_to': line.extend_to,
                                        }
                                        self.env['pms.rent_schedule'].create(val)
                                elif line.state == 'NEW' and line.end_date <= end_date and line.extend_to >= end_date + relativedelta(days=2):
                                    s_day = line.end_date.day
                                    last_day = calendar.monthrange(line.end_date.year, line.end_date.month)[1]
                                    if not start_date:
                                        start_date = line.end_date
                                    if start_date == line.end_date:
                                        date = start_date
                                        end_date = start_date + relativedelta(
                                            days=last_day - s_day)
                                        start_date = start_date + relativedelta(days=(last_day - s_day) + 1)
                                        val = {
                                            'property_id': self.property_id.id,
                                            'lease_agreement_line_id': line.id,
                                            'lease_agreement_id': self.id,
                                            'charge_type': ctype.application_id.id,
                                            'amount': ctype.total_amount,
                                            'start_date': date,
                                            'end_date': end_date,
                                            'extend_count': line.extend_count,
                                            'extend_to': line.extend_to,
                                        }
                                        self.env['pms.rent_schedule'].create(val)
                                        day = 1
                                    else:
                                        start_date = end_date + relativedelta(days = 1)
                                        l_day = calendar.monthrange(start_date.year, start_date.month)[1]
                                        end_date = end_date + relativedelta(days = l_day)
                                        if self.state == 'BOOKING' and end_date > line.end_date:
                                            end_date = line.end_date
                                        if self.state == 'NEW' and end_date > line.extend_to:
                                            end_date = line.extend_to
                                        if self.state == 'EXTENDED' and end_date > line.extend_to:
                                            end_date = line.extend_to                                    
                                        day = 1
                                        val = {
                                            'property_id': self.property_id.id,
                                            'lease_agreement_line_id': line.id,
                                            'lease_agreement_id': self.id,
                                            'charge_type': ctype.application_id.id,
                                            'amount': ctype.total_amount,
                                            'start_date': start_date,
                                            'end_date': end_date,
                                            'extend_count': line.extend_count,
                                            'extend_to': line.extend_to,
                                        }
                                        self.env['pms.rent_schedule'].create(val)
                                elif line.state == 'EXTENDED' and line.extend_to >= end_date + relativedelta(
                                            days=2):
                                    s_day = line.extend_start.day
                                    last_day = calendar.monthrange(line.extend_start.year, line.extend_start.month)[1]
                                    if not start_date:
                                        start_date = line.extend_start
                                    if start_date == line.extend_start:
                                        date = start_date
                                        end_date = start_date + relativedelta(
                                            days=last_day - s_day)
                                        start_date = start_date + relativedelta(days=(last_day - s_day) + 1)
                                        val = {
                                            'property_id': self.property_id.id,
                                            'lease_agreement_line_id': line.id,
                                            'lease_agreement_id': self.id,
                                            'charge_type': ctype.application_id.id,
                                            'amount': ctype.total_amount,
                                            'start_date': date,
                                            'end_date': end_date,
                                            'extend_count': line.extend_count,
                                            'extend_to': line.extend_to,
                                        }
                                        self.env['pms.rent_schedule'].create(val)
                                        day = 1
                                    else:
                                        start_date = end_date + relativedelta(days = 1)
                                        l_day = calendar.monthrange(start_date.year, start_date.month)[1]
                                        end_date = end_date + relativedelta(days = l_day)
                                        if self.state == 'BOOKING' and end_date > line.end_date:
                                            end_date = line.end_date
                                        if self.state == 'NEW' and end_date > line.extend_to:
                                            end_date = line.extend_to
                                        if self.state == 'EXTENDED' and end_date > line.extend_to:
                                            end_date = line.extend_to
                                        day = 1
                                        val = {
                                            'property_id': self.property_id.id,
                                            'lease_agreement_line_id': line.id,
                                            'lease_agreement_id': self.id,
                                            'charge_type': ctype.application_id.id,
                                            'amount': ctype.total_amount,
                                            'start_date': start_date,
                                            'end_date': end_date,
                                            'extend_count': line.extend_count,
                                            'extend_to': line.extend_to,
                                        }
                                        self.env['pms.rent_schedule'].create(val)
                                else:
                                    day = 0
                            else:
                                raise UserError(
                                    _("Please set start date and end date for your lease."
                                    ))
        if self.state == 'NEW':
            return self.write({'state': 'EXTENDED'})
        elif self.state == 'EXTENDED':
            return self.write({'state': 'EXTENDED'})
        else:
            val = []
            if self.lease_agreement_line:
                for lease in self.lease_agreement_line:
                    if lease.rent_schedule_line:
                        for sche in lease.rent_schedule_line:
                            val.append(sche.id)
                    lease.action_invoice(inv_type='INITIAL_PAYMENT', vals=val)
            return self.write({'state': 'NEW'})

    @api.multi
    def action_cancel(self):
        return self.write({'state': 'CANCELLED'})

    @api.multi
    def action_reset_confirm(self):
        return self.write({'state': 'BOOKING'})

    # @api.multi
    # def action_extend(self, start_date, end_date):
    #     if not self.company_id.extend_lease_term:
    #         raise UserError(
    #             _("Please set extend term in the property setting."))
    #     else:
    #         self.extend_count += 1
    #         if self.extend_count > self.company_id.extend_count:
    #             raise UserError(_("Extend Limit is Over."))
    #         # if self.extend_to:
    #         #     self.extend_to = self.extend_to + relativedelta(
    #         #         months=self.company_id.extend_lease_term.min_time_period)
    #         # else:
    #         #     self.extend_to = self.end_date + relativedelta(
    #         #         months=self.company_id.extend_lease_term.min_time_period)
    #         for d in self.lease_agreement_line:
    #             d.write({'extend_to': end_date})
    #         self._context().
    #         self.action_activate()
    #     return self.write({'extend_to': end_date,'state': 'EXTENDED'})

    def send_notify_email(self):
        partner_obj = self.env['res.partner']
        mail_mail = self.env['mail.mail']
        mail_ids = None
        today = datetime.now()    
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')    
        notify_date = new_lease_ids = extend_lease_ids = par_id = None
        for se in self.env['pms.lease_agreement'].search([]):
            notify_date = new_lease_ids = extend_lease_ids = par_id = None
            par_id = partner_obj.search([('id','=',se.company_tanent_id.id)])
            noti = None
            if se.state == 'NEW':
                noti = 'extend or renew'
                notify_date = se.end_date - relativedelta(months=se.property_id.new_lease_term.notify_period) + relativedelta(days=1)
                new_lease_ids = se.search([('end_date','=',notify_date)])
            if se.state == 'EXTENDED':
                noti = 'extend'
                notify_date = se.extend_to - relativedelta(months=se.property_id.extend_lease_term.notify_period)
                extend_lease_ids = se.search([('extend_to','=',notify_date)])
            if new_lease_ids or extend_lease_ids:
                for val in par_id:
                    email_from = val.email
                    name = val.name                
                    subject = "Mall Notify"
                    body = _("Hello %s,\n" %(name))                 
                    body += _("\tPlease Check Your Lease Agreements for Lease No(%s) to %s\n"%(se.lease_no, noti))                     
                    footer = _("Kind regards.\n")         
                    footer += _("%s\n\n"%val.company_id.name)
                    mail_ids = mail_mail.create({
                        'email_to': email_from,
                        'subject': subject,
                        'body_html': '<pre><span class="inner-pre" style="font-size: 15px">%s<br>%s</span></pre>' %(body, footer)
                        })
                    mail_ids.send()
        return None

    @api.multi
    def action_renew(self):
        line = []
        end_date = None
        if self.lease_agreement_line:
            for l in self.lease_agreement_line:
                lease_line_id = self.env['pms.lease_agreement.line'].search([
                    ('id', '=', l.id)
                ])
                for les in lease_line_id:
                    for company in self.property_id:
                        if company.new_lease_term and company.new_lease_term.lease_period_type == 'month':
                            end_date = les.end_date + relativedelta(
                                months=company.new_lease_term.min_time_period) - relativedelta(days=1)
                        elif company.new_lease_term and company.new_lease_term.lease_period_type == 'year':
                            end_date = les.end_date +relativedelta(years=company.new_lease_term.min_time_period)-relativedelta(days=1)
                    appli_ids = []
                    for ctype in les.appilication_type:
                        app_id = self.env['pms.application.charge.line'].create({
                            'id': ctype.id,
                            'application_id': ctype.application_id.id,
                            'charge_type': ctype.charge_type.id,
                            'calculatedby': ctype.calculatedby,
                            'amount': ctype.amount,
                            'total_amount': ctype.total_amount})
                        appli_ids.append(app_id.id)
                    value = {
                        'property_id':les.property_id.id,
                        'unit_no': les.unit_no.id,
                        'start_date': les.end_date,
                        'end_date': end_date,
                        'rent': les.rent,
                        'company_tanent_id': les.company_tanent_id.id,
                        'pos_id': les.pos_id,
                        'remark': les.remark,
                        'appilication_type': [(6, 0, appli_ids)],
                    }
                    line_id = self.env['pms.lease_agreement.line'].create(
                        value)
                line.append(line_id.id)
        val = {
            'name': self.name,
            'property_id': self.property_id.id,
            'company_tanent_id': self.company_tanent_id.id,
            'start_date': self.end_date,
            'end_date': end_date,
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
        if new_lease_ids:
            new_lease_ids.action_activate()
            self.write({'state': 'RENEWED'})
            return new_lease_ids.action_view_new_lease()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    @api.onchange('is_terminate')
    def onchange_is_terminate(self):
        if self.is_terminate == True:
            if not self.property_id.terminate_days:
                raise UserError(
                    _("Please set terminate days term in the property."))
            else:
                self.is_terminate = True
                self.terminate_period = (datetime.today() + relativedelta(
                    days=self.property_id.terminate_days)
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
            if property_id:
                for company in property_id:
                    if not company.lease_format:
                        raise UserError(
                            _("Please set Your Lease Format in the property setting."
                              ))
                    if company.lease_format and company.lease_format.format_line_id:
                        val = []
                        for ft in company.lease_format.format_line_id:
                            if ft.value_type == 'dynamic':
                                if property_id.code and ft.dynamic_value == 'property code':
                                    val.append(property_id.code)
                            if ft.value_type == 'fix':
                                val.append(ft.fix_value)
                            if ft.value_type == 'digit':
                                sequent_ids = self.env['ir.sequence'].search([
                                    ('name', '=', 'Lease Agreement')
                                ])
                                sequent_ids.write({'padding': ft.digit_value})
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
        # id = None
        # id = super(PMSLeaseAgreement, self).create(values)
        # if id and property_id.api_integration == True:
        #     property_obj = self.env['pms.properties'].browse(
        #         values['property_id'])
        #     integ_obj = self.env['pms.api.integration']
        #     api_type_obj = self.env['pms.api.type'].search([('name', '=',
        #                                                      "LeaseAgreement")])
        #     datas = api_rauth_config.APIData(id, values, property_obj,
        #                                      integ_obj, api_type_obj)
        # return id


class PMSLeaseAgreementLine(models.Model):
    _name = 'pms.lease_agreement.line'
    _inherit = ['mail.thread']
    _description = "Lease Agreement Line"
    _order = "id,name"

    def get_start_date(self):
        if self._context.get('start_date') != False:
            return self._context.get('start_date')

    def get_end_date(self):
        if self._context.get('end_date') != False:
            return self._context.get('end_date')

    def get_property_id(self):
        if not self.property_id:
            return self.lease_agreement_id.property_id or None

    name = fields.Char("Name", compute="compute_name", track_visibility=True)
    lease_agreement_id = fields.Many2one("pms.lease_agreement",
                                         "Lease Agreement", track_visibility=True)
    property_id = fields.Many2one("pms.properties", default=get_property_id, store=True, track_visibility=True)
    lease_no = fields.Char("Lease No", related="lease_agreement_id.lease_no", store=True, track_visibility=True)
    unit_no = fields.Many2one("pms.space.unit",
                              domain=[('status', 'in', ['vacant']),
                                      ('spaceunittype_id.chargeable', '=', True)], track_visibility=True)
    start_date = fields.Date(string="Start Date", default=get_start_date, readonly=False, store=True, track_visibility=True)
    end_date = fields.Date(string="End Date",default=get_end_date, readonly=False,  store=True, track_visibility=True)
    extend_to = fields.Date("Extend End", track_visibility=True)
    rent = fields.Float(string="Rent", related="unit_no.rate", store=True, track_visibility=True)
    company_tanent_id = fields.Many2one(
        'res.company',
        "Shop", track_visibility=True,
    )
    pos_id = fields.Char("POS ID", track_visibility=True)
    remark = fields.Text("Remark", track_visibility=True)
    rental_charge_type = fields.Selection([('base', 'Base'),
                                           ('base+gto', 'Base + GTO'),
                                           ('baseorgto', 'Base or GTO')], default='base',
                                          string="Rental Charge Type", track_visibility=True)

    rent_schedule_line = fields.One2many('pms.rent_schedule', 'lease_agreement_line_id', "Rent Schedules", track_visibility=True)
    rent_total = fields.Float("Amount(per month)", compute="get_total_rent", store=True, readonly=False, track_visibility=True)
    area = fields.Integer("Area", related="unit_no.area", track_visibility=True)
    gto_percentage = fields.Integer("GTO Percent(%)", track_visibility=True)
    maintain_charge = fields.Float("Maintain Charge", store=True, readonly=False)
    state = fields.Selection([('BOOKING', 'Booking'), ('NEW', "New"),
                              ('EXTENDED', "Extended"), ('RENEWED', 'Renewed'),
                              ('CANCELLED', "Cancelled"),
                              ('TERMINATED', 'Terminated'),
                              ('EXPIRED', "Expired")],
                             related="lease_agreement_id.state", string='Status', readonly=True, copy=False, store=True, default='BOOKING', track_visibility=True)

    invoice_count = fields.Integer(default=0, track_visibility=True)
    extend_start = fields.Date("Extend Start", store=True, track_visibility=True)
    extend_count = fields.Integer("Extend Times", related="lease_agreement_id.extend_count", store=True, track_visibility=True)
    appilication_type = fields.One2many('pms.application.charge.line','lease_line_id',"Charge Types")

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
        invoices = self.env['account.invoice'].search([('lease_no', '=', self.name)])
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
    def action_invoice(self, inv_type, vals):
        invoice_month = invoices = None
        sch_ids = start_date = end_date = []
        if inv_type == 'INITIAL_PAYMENT':
            domain_sch_ids = [('id','in',vals)]
            sch_ids= self.env['pms.rent_schedule'].search(domain_sch_ids, limit=6)
            if sch_ids:
                for sch in sch_ids:
                    start_date.append(sch.start_date)
                    end_date.append(sch.end_date)
                st_date = start_date[0]
                e_date = end_date[11]
                invoice_month = str(calendar.month_name[st_date.month])+ '/' + str(st_date.year) + ' - ' + str(calendar.month_name[e_date.month]) + '/' + str(e_date.year)
            # invoices = self.env['account.invoice'].search([('lease_no', '=', self.name)])
        if inv_type == 'MONTHLY' and vals:
            if vals[0][0] and vals[0][1]:
                invoice_month = str(calendar.month_name[vals[0][0]]) + ' - ' + str(vals[0][1])
            invoices = self.env['account.invoice'].search([('lease_no', '=', self.name), ('inv_month', '=', invoice_month)])
        if invoices:
            raise UserError(_("Already create invoice for %s in %s." %(calendar.month_name[vals[0][0]], vals[0][1])))
        else:
            invoice_lines = []
            payment_term = self.env['account.payment.term'].search([('name', '=', 'Immediate Payment')])
            product_name = product_id = prod_ids = prod_id = product_tmp_id = None
            for l in self.rent_schedule_line:
                product_name = l.lease_agreement_line_id.unit_no.name
                prod_ids = self.env['product.template'].search([('name', 'ilike', product_name)])
                prod_id = self.env['product.product'].search([('product_tmpl_id', '=', prod_ids.id)])
                if inv_type == 'MONTHLY' and vals:
                    area = rent = 0
                    if l.start_date.month == vals[0][0] and l.start_date.year == vals[0][1]:
                        if not prod_ids:
                            val = {'name': product_name,
                                'sale_ok': False,
                                'is_unit': True}
                            product_tmp_id = self.env['product.template'].create(val)
                            product_tmp_ids = self.env['product.product'].search([('product_tmpl_id', '=', product_tmp_id.id)])
                            if not product_tmp_ids:
                                product_id = self.env['product.product'].create({'product_tmpl_id': product_tmp_id.id})
                            product_id = product_tmp_ids or product_id
                        else:
                            product_id = prod_id
                        account_id = False
                        if product_id.id:
                            account_id = product_id.property_account_income_id.id or product_id.categ_id.property_account_income_categ_id.id
                        taxes = product_id.taxes_id.filtered(lambda r: not self.lease_agreement_id.company_id or r.company_id == self.lease_agreement_id.company_id)
                        unit = self.lease_agreement_id.lease_no
                        if l.charge_type.calculatedby == 'area':
                            area = self.area
                            rent = self.unit_no.min_rate
                        elif l.charge_type.calculatedby == 'fix':
                            area = 1
                            rent = l.amount
                        else:
                            area = 1
                        inv_line_id = self.env['account.invoice.line'].create({
                            'name': _(unit),
                            'account_id': account_id,
                            'price_unit': rent,
                            'quantity': area,
                            'uom_id': self.unit_no.uom.id,
                            'product_id': product_id.id,
                            'invoice_line_tax_ids': [(6, 0, taxes.ids)],
                        })
                        invoice_lines.append(inv_line_id.id)
                if inv_type == 'INITIAL_PAYMENT' and vals:
                    area = rent = 0
                    if l.start_date in start_date:
                        if not prod_ids:
                            val = {'name': product_name,
                                'sale_ok': False,
                                'is_unit': True}
                            product_tmp_id = self.env['product.template'].create(val)
                            product_tmp_ids = self.env['product.product'].search([('product_tmpl_id', '=', product_tmp_id.id)])
                            if not product_tmp_ids:
                                product_id = self.env['product.product'].create({'product_tmpl_id': product_tmp_id.id})
                            product_id = product_tmp_ids or product_id
                        else:
                            product_id = prod_id
                        account_id = False
                        if product_id.id:
                            account_id = product_id.property_account_income_id.id or product_id.categ_id.property_account_income_categ_id.id
                        taxes = product_id.taxes_id.filtered(lambda r: not self.lease_agreement_id.company_id or r.company_id == self.lease_agreement_id.company_id)
                        unit = self.lease_agreement_id.lease_no
                        if l.charge_type.calculatedby == 'area':
                            area = self.area
                            rent = self.unit_no.min_rate
                        elif l.charge_type.calculatedby == 'fix':
                            area = 1
                            rent = l.amount
                        else:
                            area = 1
                        inv_line_id = self.env['account.invoice.line'].create({
                            'name': _(unit),
                            'account_id': account_id,
                            'price_unit': rent,
                            'quantity': area,
                            'uom_id': self.unit_no.uom.id,
                            'product_id': product_id.id,
                            'invoice_line_tax_ids': [(6, 0, taxes.ids)],
                        })
                        invoice_lines.append(inv_line_id.id)
            if not invoice_lines and vals:
                raise UserError(_("No have Invoice Line for %s in %s." %(calendar.month_name[vals[0][0]], vals[0][1])))
            inv_ids = self.env['account.invoice'].create({
                'lease_no': self.name,
                'inv_month': invoice_month,
                'partner_id': self.lease_agreement_id.company_tanent_id.id,
                'property_id': self.lease_agreement_id.property_id.id,
                'company_id': self.lease_agreement_id.company_id.id,
                'payment_term_id': payment_term.id,
                'invoice_line_ids': [(6, 0, invoice_lines)],
                })
            self.invoice_count += 1
            inv_ids.action_invoice_open()
            is_email =  self.env.user.company_id.invoice_is_email
            template_id =self.env.ref('account.email_template_edi_invoice', False)
            composer = self.env['mail.compose.message'].create({'composition_mode': 'comment'})
            # active_id = self.env['account.invoice.send'].default_get({'is_email':is_email,
            #     'invoice_ids':inv_ids.id,
            #     'template_id':template_id.id,
            #     'composer_id':composer.id})
            # self.env['account.invoice.send']create({'is_email':is_email,
            #     'invoice_ids':inv_ids.id,
            #     'template_id':template_id.id,
            #     'composer_id':composer.id})
            # send_id.send_and_print_action()
            return inv_ids
    # @api.model
    # def create(self, values):
    #     # id = None
    #     # id = super(PMSLeaseAgreementLine, self).create(values)
    #     # if id and api_integration == True:
    #     #     property_obj = self.env['pms.properties'].browse(
    #     #         values['property_id'])
    #     #     integ_obj = self.env['pms.api.integration']
    #     #     api_type_obj = self.env['pms.api.type'].search([('name', '=',
    #     #                                                      "LeaseAgreementItem")])
    #     #     datas = api_rauth_config.APIData(id, values, property_obj,
    #     #                                      integ_obj, api_type_obj)
    #     return  super(PMSLeaseAgreementLine, self).create(values)


class PMSChargeTypes(models.Model):
    _name = 'pms.charge_types'
    _description = "Charge Types"

    name = fields.Char("Description", required=True, track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)
    
    @api.multi
    def toggle_active(self):
        for la in self:
            if not la.active:
                la.active = self.active
        super(PMSChargeTypes, self).toggle_active()


class PMSChargeFormula(models.Model):
    _name = 'pms.charge.formula'
    _description = "Charge Formulas"

    name = fields.Char("Description", required=True, track_visibility=True)
    code = fields.Char("Code", required=True, track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)
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

    name = fields.Char("Descritpion", required=True, track_visibility=True)
    code = fields.Char("Code", required=True, track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)

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

    name = fields.Char("Description", required=True, track_visibility=True)
    code = fields.Char("Code", required=True, track_visibility=True)
    trade_id = fields.Many2one("pms.trade_category", "Trade", track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.name
            result.append((record.id, code))
        return result

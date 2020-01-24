# -*- coding: utf-8 -*-
import calendar
from odoo import models, fields, api, tools, _
from odoo.addons.property_management_system.models import api_rauth_config


class PMSRentCharge(models.Model):
    _name = 'pms.rent_schedule'
    _description = 'Rent Schedule'
    _inherit = ['mail.thread']

    name = fields.Char("Name")
    property_id = fields.Many2one("pms.properties",
                                  "Property Name",
                                  track_visibility=True,
                                  required=True)
    lease_agreement_line_id = fields.Many2one("pms.lease_agreement.line",
                                              track_visibility=True,
                                              string="Lease Agreement Item")
    charge_type = fields.Many2one("pms.applicable.charge.type",
                                  required=True,
                                  readonly=True,
                                  track_visibility=True)
    amount = fields.Float(
        "Amount",
        track_visibility=True,
    )
    start_date = fields.Date(
        "Start Date",
        track_visibility=True,
    )
    end_date = fields.Date("End Date", track_visibility=True)
    extend_count = fields.Integer("Extend Times", store=True)
    extend_to = fields.Date('Extend To')
    lease_agreement_id = fields.Many2one("pms.lease_agreement",
                                         'Shop',
                                         track_visibility=True)
    lease_no = fields.Char("Lease", track_visibility=True)
    unit_no = fields.Many2one("pms.space.unit",
                              "Space Unit",
                              track_visibility=True)

    state = fields.Selection([('draft', "Draft"), ('generated', "Generated")],
                             "Status",
                             default="draft")
    billing_date = fields.Date(string="Billing Date", required=True)

    @api.multi
    def action_generate_rs(self):
        val = {}
        for line in self:
            if line.state == 'draft':
                val = {
                    'name': line.name,
                    'property_id': line.property_id.id,
                    'lease_agreement_id': line.lease_agreement_id.id,
                    'start_date': line.start_date,
                    'end_date': line.end_date,
                    'amount': line.amount,
                    'charge_type': line.charge_type.id,
                    'lease_no': line.lease_no,
                    'state': line.state,
                    'unit_no': line.unit_no.id,
                    'billing_date':line.billing_date,
                }
                gen_id = self.env['pms.gen.rent.schedule'].create(val)
                if gen_id:
                    line.write({'state': 'generated'})


class PMSPropertyType(models.Model):
    _name = 'pms.property.type'
    _description = 'Property Types'

    name = fields.Char("Property Type", required=True, track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)
    # property_id = fields.Many2one("pms.properties", "Property")

    _sql_constraints = [('name_unique', 'unique(name)',
                         'Your name is exiting in the database.')]

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.name
            result.append((record.id, code))
        return result

    @api.multi
    def toggle_active(self):
        for pt in self:
            if not pt.active:
                pt.active = self.active
        super(PMSPropertyType, self).toggle_active()


class PMSUtilitiesSourceType(models.Model):
    _name = "pms.utilities.source.type"
    _description = "Utilities Source Types"

    name = fields.Char("Utilities Source Type",
                       required=True,
                       track_visibility=True)
    code = fields.Char("Utilities Source Code",
                       required=True,
                       track_visibility=True)
    utilities_type_id = fields.Many2one('pms.utilities.supply.type',
                                        "Utilities Supply Type",
                                        required=True,
                                        track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)
    _sql_constraints = [('code_unique', 'unique(code)',
                         'Your name/code is exiting in the database.')]

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.code
            result.append((record.id, code))
        return result

    @api.multi
    def toggle_active(self):
        for st in self:
            if not st.active:
                st.active = self.active
        super(PMSUtilitiesSourceType, self).toggle_active()


class PMSUtilitiesSupplyType(models.Model):
    _name = "pms.utilities.supply.type"
    _description = "Utilities Supply Types"
    _order = 'ordinal_no,name'

    name = fields.Char("Utilities Supply Type",
                       required=True,
                       track_visibility=True)
    code = fields.Char("Utilities Supply Code",
                       required=True,
                       track_visibility=True)
    ordinal_no = fields.Integer("Ordinal No")
    active = fields.Boolean(default=True, track_visibility=True)
    _sql_constraints = [('code_unique', 'unique(code)',
                         'Your code is exiting in the database.')]

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.code
            result.append((record.id, code))
        return result

    @api.multi
    def toggle_active(self):
        for pt in self:
            if not pt.active:
                pt.active = self.active
        super(PMSUtilitiesSupplyType, self).toggle_active()


class PMSFacilitiesline(models.Model):
    _name = 'pms.facility.lines'
    _description = "Facility Lines"

    def get_property_id(self):
        if self._context.get('property_id') != False:
            return self._context.get('property_id')

    facility_id = fields.Many2one("pms.facilities",
                                  "Facilities",
                                  track_visibility=True)
    source_type_id = fields.Many2one('pms.utilities.source.type',
                                     "Utilities Source Type",
                                     required=True,
                                     track_visibility=True)
    # install_date = fields.Date("Install Date", track_visibility=True)
    lmr_date = fields.Date("Last Reading Date", track_visibility=True)
    lmr_value = fields.Float("Last Reading Value", track_visibility=True)
    # digit = fields.Integer("Digit", track_visibility=True)
    end_date = fields.Date("End Date", track_visibility=True)
    status = fields.Boolean("Status", default=True, track_visibility=True)
    property_id = fields.Many2one("pms.properties",
                                  "Property",
                                  default=get_property_id,
                                  required=True,
                                  store=True,
                                  track_visibility=True)

    @api.onchange('source_type_id')
    def onchange_source_type_id(self):
        uti_ids = lst = []
        domain = {}
        if self.facility_id.utilities_type_id:
            utilities_ids = self.env['pms.utilities.source.type'].search([
                ('utilities_type_id', '=',
                 self.facility_id.utilities_type_id.id)
            ])
            for uti in utilities_ids:
                uti_ids.append(uti.id)
            domain = {'source_type_id': [('id', 'in', uti_ids)]}
        return {'domain': domain}

    # @api.model
    # def create(self, values):
    #     id = None
    #     id = super(PMSFacilitiesline, self).create(values)
    #     if id:
    #         property_obj = self.env['pms.properties'].browse(
    #             values['property_id'])
    #         integ_obj = self.env['pms.api.integration']
    #         api_type_obj = self.env['pms.api.type'].search([('name', '=',
    #                                                          "FacilitieLine")])
    #         datas = api_rauth_config.APIData(id, values, property_obj,
    #                                          integ_obj, api_type_obj)
    #     return id


class PMSSpaceUntiManagement(models.Model):
    _name = 'pms.space.unit.management'
    _description = "Space Unit Management"

    name = fields.Char(
        "Name",
        default="New",
        readonly=True,
    )
    floor_id = fields.Many2one("pms.floor", "Floor", track_visibility=True)
    space_unit_id = fields.Many2one("pms.space.unit",
                                    "From Unit",
                                    track_visibility=True)
    area = fields.Integer("Area", track_visibility=True)
    no_of_unit = fields.Integer("No of Unit", track_visibility=True)
    to_unit = fields.Char("To Unit", track_visibility=True)
    combination_type = fields.Selection([('random', 'Random'),
                                         ('range', 'Range')],
                                        "Combination Type",
                                        track_visibility=True)
    action_type = fields.Selection([('division', 'Division'),
                                    ('combination', 'Combination')],
                                   "Action Type",
                                   default="division",
                                   track_visibility=True)
    state = fields.Selection([('draft', "Draft"), ('done', "Done")],
                             "Status",
                             default="draft",
                             track_visibility=True)
    space_unit = fields.Many2many("pms.space.unit",
                                  string="Unit",
                                  track_visibility=True)

    @api.multi
    def action_division(self):
        if self.state == 'draft':
            self.state = "done"

    @api.multi
    def action_combination(self):
        if self.state == 'draft':
            self.state = "done"


class PMSDisplayType(models.Model):
    _name = "pms.display.type"
    _description = 'Display Type'

    name = fields.Char("Name", track_visibility=True)
    code = fields.Char("Code", track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.code
            result.append((record.id, code))
        return result


# class PMSMeterType(models.Model):
#     _name = "pms.meter.type"
#     _description = 'Meter Type'

#     name = fields.Char("Meter No")
#     utilities_id = fields.Many2one("pms.utilities.type", "utilities Type")
#     display_type = fields.Many2one('pms.display.type', 'Display Type')
#     digit = fields.Selection([('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'),
#                               ('7', '7'), ('8', '8'), ('9', '9')],
#                              "Display Digits")
#     charge_type = fields.Selection([('fixed', 'Fixed'),
#                                     ('variable', 'Variable')],
#                                    string="Charge Type")


class PMSTerms(models.Model):
    _name = "pms.terms"
    _description = 'Terms'

    name = fields.Char("Name",
                       default="New",
                       readonly=True,
                       track_visibility=True)
    space_unit_fromat_id = fields.Many2one("pms.format",
                                           string="Unit Code Format",
                                           track_visibility=True)
    pos_id_format_id = fields.Many2one("pms.format",
                                       string="POS ID Format",
                                       track_visibility=True)
    company_id = fields.Many2one("res.company",
                                 string="Company",
                                 track_visibility=True)
    is_auto_generate_posid = fields.Boolean("Auto Generate POS ID",
                                            track_visibility=True)
    property_code_len = fields.Integer("Property Code Len",
                                       track_visibility=True)
    floor_code_len = fields.Integer("Floor Code Len", track_visibility=True)
    space_unit_code_len = fields.Integer("Space Unit Code Len",
                                         track_visibility=True)
    active = fields.Boolean("Active", default=True, track_visibility=True)

    @api.multi
    def toggle_active(self):
        for pt in self:
            if not pt.active:
                pt.active = self.active
        super(PMSTerms, self).toggle_active()


# class PMSBank(models.Model):
#     _name = 'pms.bank'
#     _description = "Bank"

#     country = fields.Many2one("pms.country",
#                               "Country Name",
#                               track_visibility=True)
#     city_id = fields.Many2one("pms.city", "City Name", track_visibility=True)
#     state_id = fields.Many2one("pms.state",
#                                "State Name",
#                                track_visibility=True)
#     name = fields.Char("Name", track_visibility=True)
#     bic = fields.Char("Bank Identifier Code", track_visibility=True)
#     phone = fields.Char("Phone", track_visibility=True)
#     email = fields.Char("Email", track_visibility=True)
#     no = fields.Char("No", track_visibility=True)
#     street = fields.Char("Street", track_visibility=True)
#     zip_code = fields.Char("Zip", track_visibility=True)
#     active = fields.Char(default=True, track_visibility=True)


class Bank(models.Model):
    _inherit = 'res.bank'

    bic = fields.Char('Switch Code',
                      index=True,
                      track_visibility=True,
                      help="Sometimes called BIC or Swift.")
    branch = fields.Char("Branch Name",
                         index=True,
                         track_visibility=True,
                         help="Sometimes called BIC or Swift.")
    city_id = fields.Many2one("pms.city",
                              "City Name",
                              track_visibility=True,
                              ondelete='cascade')
    township = fields.Many2one("pms.township",
                               "Township",
                               track_visibility=True)

    _sql_constraints = [('name_unique', 'unique(name)',
                         'Your name is exiting in the database.')]


class PMSCity(models.Model):
    _name = "pms.city"
    _description = "City"
    _order = "code,name"

    state_id = fields.Many2one("res.country.state",
                               "State Name",
                               required=True,
                               track_visibility=True)
    name = fields.Char("City Name", required=True, track_visibility=True)
    code = fields.Char("City Code", required=True, track_visibility=True)


class Company(models.Model):
    _inherit = "res.company"
    _description = 'Companies'
    _order = 'sequence, name'

    city_id = fields.Many2one("pms.city",
                              "City Name",
                              compute='_compute_address',
                              inverse='_inverse_city',
                              track_visibility=True,
                              ondelete='cascade')
    township = fields.Many2one("pms.township",
                               "Township Name",
                               compute='_compute_address',
                               inverse='_inverse_township',
                               track_visibility=True,
                               ondelete='cascade')
    company_type = fields.Many2many('pms.company.category',
                                    "res_company_type_rel",
                                    'company_id',
                                    'category_id',
                                    track_visibility=True)

    def _get_company_address_fields(self, partner):
        return {
            'street': partner.street,
            'street2': partner.street2,
            'township': partner.township,
            'city_id': partner.city_id,
            'zip': partner.zip,
            'state_id': partner.state_id,
            'country_id': partner.country_id,
        }

    def _inverse_township(self):
        for company in self:
            company.partner_id.township = company.township


# class PMSTownship(models.Model):
#     _name = "pms.township"
#     _description = "Township"

#     city_id = fields.Many2one("pms.city","City Name",required=True)
#     name = fields.Char("Township Name", required=True)
#     code = fields.Char("Township Code", required=True)


class PMSTownship(models.Model):
    _name = "pms.township"
    _description = "Township"
    _order = "code,name"

    name = fields.Char("Name", required=True, track_visibility=True)
    code = fields.Char("Code", required=True, track_visibility=True)
    city_id = fields.Many2one("pms.city",
                              "City",
                              ondelete='cascade',
                              required=True,
                              track_visibility=True)


class PMSState(models.Model):
    _name = "pms.state"
    _description = "State"

    country_id = fields.Many2one("pms.country",
                                 "Country Name",
                                 required=True,
                                 track_visibility=True)
    name = fields.Char("State Name", required=True, track_visibility=True)
    code = fields.Char("State Code", required=True, track_visibility=True)


class PMSCountry(models.Model):
    _name = "pms.country"
    _description = "Country"

    name = fields.Char("Country Name", required=True, track_visibility=True)
    code = fields.Char("Country Code", required=True, track_visibility=True)


class PMSCurrency(models.Model):
    _name = "pms.currency"
    _description = "Currency"

    name = fields.Char("Name", required=True, track_visibility=True)
    symbol = fields.Char("Symbol", required=True, track_visibility=True)
    status = fields.Boolean("Active", track_visibility=True)

    @api.multi
    def action_status(self):
        if self.status is True:
            self.status = False
        else:
            self.status = True


class PMSCompany(models.Model):
    _name = "pms.company"
    _description = "Company"

    name = fields.Char("Name", required=True, track_visibility=True)


class PMSDepartment(models.Model):
    _name = "pms.department"
    _description = "Department"
    _order = "name"

    name = fields.Char("Name", required=True, track_visibility=True)
    parent_id = fields.Many2one("pms.department",
                                "Parent Department",
                                track_visibility=True)


class PMSCompanyCategory(models.Model):
    _name = "pms.company.category"
    _description = "Company Categorys"

    name = fields.Char("Description", required=True, track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)

    @api.multi
    def toggle_active(self):
        for ct in self:
            if not ct.active:
                ct.active = self.active
        super(PMSCompanyCategory, self).toggle_active()


class Partner(models.Model):
    _inherit = "res.partner"

    city_id = fields.Many2one("pms.city", "City Name", track_visibility=True)
    company_type = fields.Selection(
        string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company')],
        compute='_compute_company_type',
        inverse='_write_company_type',
        track_visibility=True,
    )
    # type = fields.Selection(
    #     [('contact', 'Contact'), ('invoice', 'Invoice')],
    #     string='Address Type',
    #     default='contact',
    # )
    child_ids = fields.One2many('res.partner',
                                'parent_id',
                                string='Contacts',
                                track_visibility=True,
                                domain=[('is_company', '!=', True)])
    company_channel_type = fields.Many2many('pms.company.category',
                                            string="CRM Type",
                                            track_visibility=True)
    township = fields.Many2one('pms.township',
                               "Township",
                               track_visibility=True)
    is_tanent = fields.Boolean('Is Tanent',
                               compute="get_tanent",
                               readonly=False,
                               store=True,
                               track_visibility=True)
    # partner_contact_id = fields.Many2many(
    #     "res.partner",
    #     "company_partner_contact_rel",
    #     "company_id",
    #     "partner_id",
    #     domain="[('is_company', '!=', True)]",
    #     store=True)
    trade_id = fields.Many2one("pms.trade_category",
                               "Trade",
                               track_visibility=True)
    sub_trade_id = fields.Many2one("pms.sub_trade_category",
                                   "Sub Trade",
                                   track_visibility=True)

    @api.one
    @api.depends('company_channel_type')
    def get_tanent(self):
        category = []
        if self.company_channel_type:
            for comp in self.company_channel_type:
                for cat in comp:
                    category.append(cat.name)
                if 'Tenant' in category:
                    self.is_tanent = True

    @api.depends('is_company')
    def _compute_company_type(self):
        for partner in self:
            if partner.is_company or self._context.get(
                    'default_company_type') == 'company':
                partner.company_type = 'company'
                partner.is_company = True
            else:
                partner.company_type = 'person'

    def _write_company_type(self):
        for partner in self:
            partner.is_company = partner.company_type == 'company'


class PMSGenerateRentSchedule(models.Model):
    _name = "pms.gen.rent.schedule"
    _description = "Generate Rent Schedule"
    _inherit = ['mail.thread']

    name = fields.Char("Name")
    property_id = fields.Many2one("pms.properties",
                                  "Property Name",
                                  track_visibility=True,
                                  required=True)
    lease_agreement_line_id = fields.Many2one("pms.lease_agreement.line",
                                              track_visibility=True,
                                              string="Lease Agreement Item")
    charge_type = fields.Many2one("pms.applicable.charge.type",
                                  required=True,
                                  readonly=True,
                                  track_visibility=True)
    amount = fields.Float(
        "Amount",
        track_visibility=True,
    )
    start_date = fields.Date(
        "Start Date",
        track_visibility=True,
    )
    end_date = fields.Date("End Date", track_visibility=True)
    extend_count = fields.Integer("Extend Times", store=True)
    extend_to = fields.Date('Extend To')
    lease_agreement_id = fields.Many2one("pms.lease_agreement",
                                         'Shop',
                                         track_visibility=True)
    lease_no = fields.Char("Lease", track_visibility=True)
    unit_no = fields.Many2one("pms.space.unit",
                              "Space Unit",
                              track_visibility=True)

    state = fields.Selection([('draft', "Draft"), ('submitted', "Submitted"),
                              ('confirmed', "Confirmed"),
                              ('invoiced', "Invoiced")],
                             "Status",
                             default="draft", track_visibility=True)
    billing_date = fields.Date(string="Billing Date", required=True)

    @api.multi
    def action_confirm(self):
        if len(self) > 1:
            for line in self:
                if line.state == 'submitted':
                    line.write({'state': 'confirmed'})
        else:
            if self.state == 'submitted':
                self.write({'state': 'confirmed'})

    @api.multi
    def action_submit(self):
        if len(self) > 1:
            for line in self:
                if line.state == 'draft':
                    line.write({'state': 'submitted'})
        else:
            if self.state == 'draft':
                self.write({'state': 'submitted'})

    @api.multi
    def action_reject(self):
        if len(self) > 1:
            for line in self:
                if line.state == 'submitted':
                    line.write({'state': 'draft'})
        else:
            if self.state == 'submitted':
                self.write({'state': 'draft'})

    @api.multi
    def action_create_invoice(self):
        invoice_month = unit =  None
        for ls in self:
            invoice_lines = []
            if ls.state == 'confirmed':
                invoice_month = str(calendar.month_name[ls.billing_date.month]) + ' - ' + str(ls.billing_date.year)
                for line in self:
                    product_name = None
                    if line.property_id == ls.property_id and line.billing_date == ls.billing_date and line.lease_no == ls.lease_no:
                        product_name = line.charge_type.name
                        prod_ids = self.env['product.template'].search([('name', 'ilike', product_name)])
                        prod_id = self.env['product.product'].search([('product_tmpl_id', '=', prod_ids.id)])
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
                        account_id = product_id.property_account_income_id.id or product_id.categ_id.property_account_income_categ_id.id
                        taxes = product_id.taxes_id.filtered(lambda r: not line.lease_agreement_id.company_id or r.company_id == line.lease_agreement_id.company_id)
                        unit = line.lease_agreement_id.unit_no
                        inv_line_id = self.env['account.invoice.line'].create({
                            'name': _(product_name),
                            'account_id': account_id,
                            'price_unit': line.amount,
                            'quantity': 1,
                            'uom_id': product_id.uom_id.id,
                            'product_id': product_id.id,
                            'invoice_line_tax_ids': [(6, 0, taxes.ids)],
                        })
                        invoice_lines.append(inv_line_id.id)
                        line.write({'state': 'invoiced'})
                inv_ids = self.env['account.invoice'].create({
                    'lease_items': ls.name,
                    'lease_no': ls.lease_agreement_id.lease_no,
                    'unit_no': unit,
                    'inv_month': invoice_month,
                    'partner_id': ls.lease_agreement_id.company_tanent_id.id,
                    'property_id': ls.lease_agreement_id.property_id.id,
                    'company_id': ls.lease_agreement_id.company_id.id,
                    'invoice_line_ids': [(6, 0, invoice_lines)],
                    })
            # datas.append(inv_ids.id)
            # self.invoice_count += 1
            # inv_ids.action_invoice_open()
        return True


    # def action_invoice(self, vals):
    #     invoice_month = invoices = None
    #     sch_ids = start_date = end_date = []
    #     if vals[0][0] and vals[0][1]:
    #         invoice_month = str(calendar.month_name[vals[0][0]]) + ' - ' + str(vals[0][1])
    #     invoices = self.env['account.invoice'].search([('lease_items', '=', self.name), ('inv_month', '=', invoice_month)])
    #     if invoices:
    #         raise UserError(_("Already create invoice for %s in %s." %(calendar.month_name[vals[0][0]], vals[0][1])))
    #     else:
    #         invoice_lines = []
    #         payment_term = self.env['account.payment.term'].search([('name', '=', 'Immediate Payment')])
    #         product_name = product_id = prod_ids = prod_id = product_tmp_id = None
    #         for l in self.rent_schedule_line:
    #             product_name = l.lease_agreement_line_id.unit_no.name
    #             prod_ids = self.env['product.template'].search([('name', 'ilike', product_name)])
    #             prod_id = self.env['product.product'].search([('product_tmpl_id', '=', prod_ids.id)])
    #             if inv_type == 'MONTHLY' and vals:
    #                 area = rent = 0
    #                 if l.start_date.month == vals[0][0] and l.start_date.year == vals[0][1]:
    #                     if not prod_ids:
    #                         val = {'name': product_name,
    #                             'sale_ok': False,
    #                             'is_unit': True}
    #                         product_tmp_id = self.env['product.template'].create(val)
    #                         product_tmp_ids = self.env['product.product'].search([('product_tmpl_id', '=', product_tmp_id.id)])
    #                         if not product_tmp_ids:
    #                             product_id = self.env['product.product'].create({'product_tmpl_id': product_tmp_id.id})
    #                         product_id = product_tmp_ids or product_id
    #                     else:
    #                         product_id = prod_id
    #                     account_id = False
    #                     if product_id.id:
    #                         account_id = product_id.property_account_income_id.id or product_id.categ_id.property_account_income_categ_id.id
    #                     taxes = product_id.taxes_id.filtered(lambda r: not self.lease_agreement_id.company_id or r.company_id == self.lease_agreement_id.company_id)
    #                     unit = self.lease_agreement_id.lease_no
    #                     if l.charge_type.calcuation_method.name == 'area':
    #                         area = 1
    #                         rent = l.amount
    #                     elif l.charge_type.calcuation_method.name == 'meter_unit':
    #                         area = 1
    #                         rent = l.amount
    #                     else:
    #                         area = 1
    #                         rent = l.amount
    #                     inv_line_id = self.env['account.invoice.line'].create({
    #                         'name': _(l.charge_type.name),
    #                         'account_id': account_id,
    #                         'price_unit': rent,
    #                         'quantity': area,
    #                         'uom_id': self.unit_no.uom.id,
    #                         'product_id': product_id.id,
    #                         'invoice_line_tax_ids': [(6, 0, taxes.ids)],
    #                     })
    #                     invoice_lines.append(inv_line_id.id)
    #             if inv_type == 'INITIAL_PAYMENT' and vals:
    #                 area = rent = 0
    #                 if l.start_date in start_date:
    #                     if not prod_ids:
    #                         val = {'name': product_name,
    #                             'sale_ok': False,
    #                             'is_unit': True}
    #                         product_tmp_id = self.env['product.template'].create(val)
    #                         product_tmp_ids = self.env['product.product'].search([('product_tmpl_id', '=', product_tmp_id.id)])
    #                         if not product_tmp_ids:
    #                             product_id = self.env['product.product'].create({'product_tmpl_id': product_tmp_id.id})
    #                         product_id = product_tmp_ids or product_id
    #                     else:
    #                         product_id = prod_id
    #                     account_id = False
    #                     if product_id.id:
    #                         account_id = product_id.property_account_income_id.id or product_id.categ_id.property_account_income_categ_id.id
    #                     taxes = product_id.taxes_id.filtered(lambda r: not self.lease_agreement_id.company_id or r.company_id == self.lease_agreement_id.company_id)
    #                     unit = self.lease_agreement_id.lease_no
    #                     if l.charge_type.calcuation_method.name == 'area':
    #                         area = 1
    #                         rent = l.amount
    #                     elif l.charge_type.calcuation_method.name == 'meter_unit':
    #                         area = 1
    #                         rent = l.amount
    #                     else:
    #                         area = 1
    #                         rent = l.amount
    #                     inv_line_id = self.env['account.invoice.line'].create({
    #                         'name': _(l.charge_type.name),
    #                         'account_id': account_id,
    #                         'price_unit': rent,
    #                         'quantity': area,
    #                         'uom_id': self.unit_no.uom.id,
    #                         'product_id': product_id.id,
    #                         'invoice_line_tax_ids': [(6, 0, taxes.ids)],
    #                     })
    #                     invoice_lines.append(inv_line_id.id)
    #         if not invoice_lines and vals:
    #             raise UserError(_("No have Invoice Line for %s in %s." %(calendar.month_name[vals[0][0]], vals[0][1])))
    #         inv_ids = self.env['account.invoice'].create({
    #             'lease_items':self.name,
    #             'lease_no': self.lease_agreement_id.lease_no,
    #             'unit_no': self.lease_agreement_id.unit_no,
    #             'inv_month': invoice_month,
    #             'partner_id': self.lease_agreement_id.company_tanent_id.id,
    #             'property_id': self.lease_agreement_id.property_id.id,
    #             'company_id': self.lease_agreement_id.company_id.id,
    #             'payment_term_id': payment_term.id,
    #             'invoice_line_ids': [(6, 0, invoice_lines)],
    #             })
    #         self.invoice_count += 1
    #         inv_ids.action_invoice_open()
    #         is_email =  self.env.user.company_id.invoice_is_email
    #         template_id =self.env.ref('account.email_template_edi_invoice', False)
    #         composer = self.env['mail.compose.message'].create({'composition_mode': 'comment'})
    #         return inv_ids

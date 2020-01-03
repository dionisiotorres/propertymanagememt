# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from odoo.addons.property_management_system.models import api_rauth_config


class PMSRentCharge(models.Model):
    _name = 'pms.rent_schedule'
    _description = 'Rent Schedule'

    property_id = fields.Many2one("pms.properties",
                                  "Property ID",
                                  track_visibility=True,
                                  required=True)
    lease_agreement_line_id = fields.Many2one("pms.lease_agreement.line",
                                              track_visibility=True,
                                              string="Lease Agreement Item")
    charge_type = fields.Selection(
        [('base', 'Base'), ('base+gto', 'Base + GTO'),
         ('baseorgto', 'Base or GTO')],
        string="Charge Type",
        track_visibility=True,
    )
    gto_amount = fields.Float(
        "Gto Amount",
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
                                         'Lease Agreement',
                                         track_visibility=True)
    unit_no = fields.Many2one("pms.space.unit",
                              "Space Unit",
                              track_visibility=True)

    # paid = fields.Boolean("")


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


class PMSUtilitySourceType(models.Model):
    _name = "pms.utility.source.type"
    _description = "Utility Source Types"

    name = fields.Char("Description", required=True, track_visibility=True)
    code = fields.Char("Code", required=True, track_visibility=True)
    utility_type_id = fields.Many2one('pms.utility.supply.type',
                                      "Utility Supply Type",
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
        super(PMSSupplierType, self).toggle_active()


class PMSUtilitySupplyType(models.Model):
    _name = "pms.utility.supply.type"
    _description = "Utility Supply Types"

    name = fields.Char("Utility Name", required=True, track_visibility=True)
    code = fields.Char("Utility Code", required=True, track_visibility=True)
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
        super(PMSUtilityType, self).toggle_active()


class PMSFacilitiesline(models.Model):
    _name = 'pms.facility.lines'
    _description = "Facility Lines"

    def get_property_id(self):
        if self._context.get('property_id') != False:
            return self._context.get('property_id')

    facility_id = fields.Many2one("pms.facilities",
                                  "Facilities",
                                  track_visibility=True)
    supplier_type_id = fields.Many2one('pms.utility.source.type',
                                       "Utility Source Type",
                                       required=True,
                                       track_visibility=True)
    # install_date = fields.Date("Install Date", track_visibility=True)
    start_reading_value = fields.Integer("Last Reading Value",
                                         track_visibility=True)
    # digit = fields.Integer("Digit", track_visibility=True)
    start_date = fields.Date("Start Date", track_visibility=True)
    end_date = fields.Date("End Date", track_visibility=True)
    status = fields.Boolean("Status", default=True, track_visibility=True)
    property_id = fields.Many2one("pms.properties",
                                  "Property",
                                  default=get_property_id,
                                  required=True,
                                  store=True,
                                  track_visibility=True)

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

    name = fields.Char("Name",
                       default="New",
                       readonly=True,)
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
#     utility_id = fields.Many2one("pms.utility.type", "Utility Type")
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


class PMSBank(models.Model):
    _name = 'pms.bank'
    _description = "Bank"

    country = fields.Many2one("pms.country",
                              "Country Name",
                              track_visibility=True)
    city_id = fields.Many2one("pms.city", "City Name", track_visibility=True)
    state_id = fields.Many2one("pms.state",
                               "State Name",
                               track_visibility=True)
    name = fields.Char("Name", track_visibility=True)
    bic = fields.Char("Bank Identifier Code", track_visibility=True)
    phone = fields.Char("Phone", track_visibility=True)
    email = fields.Char("Email", track_visibility=True)
    no = fields.Char("No", track_visibility=True)
    street = fields.Char("Street", track_visibility=True)
    zip_code = fields.Char("Zip", track_visibility=True)
    active = fields.Char(default=True, track_visibility=True)


class Bank(models.Model):
    _inherit = 'res.bank'

    bic = fields.Char('Switch Code',
                      index=True, track_visibility=True,
                      help="Sometimes called BIC or Swift.")
    branch = fields.Char("Branch Name",
                         index=True, track_visibility=True,
                         help="Sometimes called BIC or Swift.")
    city_id = fields.Many2one("pms.city", "City Name", track_visibility=True, ondelete='cascade')
    township = fields.Many2one("pms.township", "Township", track_visibility=True)

    _sql_constraints = [('name_unique', 'unique(name)',
                         'Your name is exiting in the database.')]


class PMSCity(models.Model):
    _name = "pms.city"
    _description = "City"
    _order = "code,name"

    state_id = fields.Many2one("res.country.state",
                               "State Name",
                               required=True, track_visibility=True)
    name = fields.Char("City Name", required=True, track_visibility=True)
    code = fields.Char("City Code", required=True, track_visibility=True)


class Company(models.Model):
    _inherit = "res.company"
    _description = 'Companies'
    _order = 'sequence, name'

    city_id = fields.Many2one("pms.city",
                              "City Name",
                              compute='_compute_address',
                              inverse='_inverse_city', track_visibility=True,
                              ondelete='cascade')
    township = fields.Many2one("pms.township",
                               "Township Name",
                               compute='_compute_address',
                               inverse='_inverse_township', track_visibility=True,
                               ondelete='cascade')
    company_type = fields.Many2many('pms.company.category',
                                    "res_company_type_rel", 'company_id',
                                    'category_id', track_visibility=True)

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
                              required=True, track_visibility=True)


class PMSState(models.Model):
    _name = "pms.state"
    _description = "State"

    country_id = fields.Many2one("pms.country", "Country Name", required=True, track_visibility=True)
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
    parent_id = fields.Many2one("pms.department", "Parent Department", track_visibility=True)


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
        inverse='_write_company_type', track_visibility=True,
    )
    # type = fields.Selection(
    #     [('contact', 'Contact'), ('invoice', 'Invoice')],
    #     string='Address Type',
    #     default='contact',
    # )
    child_ids = fields.One2many('res.partner',
                                'parent_id',
                                string='Contacts', track_visibility=True,
                                domain=[('is_company', '!=', True)])
    company_channel_type = fields.Many2many('pms.company.category',
                                            string="Type", track_visibility=True)
    township = fields.Many2one('pms.township', "Township", track_visibility=True)
    is_tanent = fields.Boolean('Is Tanent',
                               compute="get_tanent",
                               readonly=False,
                               store=True, track_visibility=True)
    # partner_contact_id = fields.Many2many(
    #     "res.partner",
    #     "company_partner_contact_rel",
    #     "company_id",
    #     "partner_id",
    #     domain="[('is_company', '!=', True)]",
    #     store=True)
    trade_id = fields.Many2one("pms.trade_category", "Trade", track_visibility=True)
    sub_trade_id = fields.Many2one("pms.sub_trade_category", "Sub Trade", track_visibility=True)

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

    # dis_company_type = fields.Boolean("Disable")
    # department_id = fields.Many2one(
    #     "pms.department",
    #     "Department",
    #     help="Department is set the partner department.")

# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools


class PMSEquipmentType(models.Model):
    _name = 'pms.equipment.type'
    _description = 'Equipment Types'

    name = fields.Char("Equipment Type", required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [('name_unique', 'unique(name)',
                         'Your name is exiting in the database.')]


class PMSEquipment(models.Model):
    _name = 'pms.equipment'
    _description = "Equipments"

    equipment_type_id = fields.Many2one("pms.equipment.type",
                                        string="Equipment Type",
                                        required=True)
    name = fields.Char("Serial No", required=True)
    model = fields.Char("Model", required=True)
    manufacutrue = fields.Char("Manufacture")
    ref_code = fields.Char("RefCode")
    active = fields.Boolean(default=True)


class PMSPropertyType(models.Model):
    _name = 'pms.property.type'
    _description = 'Property Types'

    name = fields.Char("Property Type", required=True)
    active = fields.Boolean(default=True)

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

    name = fields.Char("Description", required=True)
    code = fields.Char("Code", required=True)
    utility_type_id = fields.Many2one('pms.utility.supply.type',
                                      "Utility Supply Type",
                                      required=True)
    active = fields.Boolean(default=True)
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

    name = fields.Char("Utility Name", required=True)
    code = fields.Char("Utility Code", required=True)
    active = fields.Boolean(default=True)
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


class PMSFacilities(models.Model):
    _name = 'pms.facilities'
    _description = "Facilities"

    name = fields.Char(default="New",
                       related='meter_no.name',
                       readonly=True,
                       store=True,
                       required=True)
    utility_type_id = fields.Many2one('pms.utility.supply.type',
                                      "Utility Supply Type",
                                      required=True)
    meter_no = fields.Many2one("pms.equipment", "Meter No", required=True)
    interface_type = fields.Selection([('auto', 'Auto'), ('manual', 'Manual'),
                                       ('mobile', 'Mobile')], "Interface Type")
    remark = fields.Text("Remark")
    status = fields.Boolean("Status", default=True)
    facilities_line = fields.One2many("pms.facility.lines", "facility_id",
                                      "Facility Lines")
    _sql_constraints = [('name_unique', 'unique(name)',
                         'Your name is exiting in the database.')]

    # @api.onchange('utility_type_id')
    # def onchange_utility_type_id(self):
    #     parent_id = []
    #     domain = {}
    #     utility_id = None
    #     if self.utility_type_id != None:
    #         utility_ids = self.env['pms.utility.source.type'].search([
    #             ('utility_type_id', '=', self.utility_type_id.id)
    #         ])
    #         for loop in utility_ids:
    #             parent_id.append(loop.id)
    #         domain = {'supplier_type_id': [('id', 'in', parent_id)]}
    #     return {'domain': domain}


class PMSFacilitiesline(models.Model):
    _name = 'pms.facility.lines'
    _description = "Facility Lines"

    facility_id = fields.Many2one("pms.facilities", "Facilities")
    supplier_type_id = fields.Many2one('pms.utility.source.type',
                                       "Utility Source Type",
                                       required=True)
    install_date = fields.Date("Install Date")
    start_reading_value = fields.Integer("Last Reading Value")
    digit = fields.Integer("Digit")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    status = fields.Boolean("Status", default=True)

    # @api.onchange('supplier_type_id')
    # def onchange_supplier_type_id(self):
    #     parent = []
    #     domain = {}
    #     if self.utility_type_id:
    #         supplier_ids = self.env['pms.supplier.type'].search([
    #             ('utility_type_id', '=', self.utility_type_id.id)
    #         ])
    #         for s in supplier_ids:
    #             parent.append(s.id)
    #         domain = {'supplier_type_id': [('id', 'in', parent)]}
    #     return {'domain': domain}


class PMSSpaceUntiManagement(models.Model):
    _name = 'pms.space.unit.management'
    _description = "Space Unit Management"

    name = fields.Char("Name", default="New", readonly=True)
    floor_id = fields.Many2one("pms.floor", "Floor")
    space_unit_id = fields.Many2one("pms.space.unit", "From Unit")
    area = fields.Integer("Area")
    no_of_unit = fields.Integer("No of Unit")
    to_unit = fields.Char("To Unit")
    combination_type = fields.Selection(
        [('random', 'Random'), ('range', 'Range')],
        "Combination Type",
    )
    action_type = fields.Selection([('division', 'Division'),
                                    ('combination', 'Combination')],
                                   "Action Type",
                                   default="division")
    state = fields.Selection([('draft', "Draft"), ('done', "Done")],
                             "Status",
                             default="draft")
    space_unit = fields.Many2many("pms.space.unit", string="Unit")

    @api.multi
    def action_division(self):
        if self.state == 'draft':
            self.state = "done"

    @api.multi
    def action_combination(self):
        if self.state == 'draft':
            self.state = "done"


class PMSSpaceType(models.Model):
    _name = 'pms.space.type'
    _description = 'Space Type'

    name = fields.Char("Name", required=True)
    chargeable = fields.Boolean("Chargeable")
    divisible = fields.Boolean("Divisible")


class PMSDisplayType(models.Model):
    _name = "pms.display.type"
    _description = 'Display Type'

    name = fields.Char("Name")
    code = fields.Char("Code")
    active = fields.Boolean(default=True)

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

    name = fields.Char("Name", default="New", readonly=True)
    space_unit_fromat_id = fields.Many2one("pms.format",
                                           string="Unit Code Format")
    pos_id_format_id = fields.Many2one("pms.format", string="POS ID Format")
    company_id = fields.Many2one("res.company", string="Company")
    is_auto_generate_posid = fields.Boolean("Auto Generate POS ID")
    property_code_len = fields.Integer("Property Code Len")
    floor_code_len = fields.Integer("Floor Code Len")
    space_unit_code_len = fields.Integer("Space Unit Code Len")
    active = fields.Boolean("Active", default=True)

    @api.multi
    def toggle_active(self):
        for pt in self:
            if not pt.active:
                pt.active = self.active
        super(PMSTerms, self).toggle_active()


class PMSUom(models.Model):
    _name = "pms.uom"
    _description = "UOM"
    _order = "name"

    name = fields.Char("Name", required=True)
    category_id = fields.Many2one("pms.uom.category",
                                  "Category",
                                  required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [('name_unique', 'unique(name)',
                         'Your name is exiting in the database.')]

    @api.multi
    def toggle_active(self):
        for pt in self:
            if not pt.active:
                pt.active = self.active
        super(PMSUom, self).toggle_active()


class PMSUomCategory(models.Model):
    _name = "pms.uom.category"
    _description = "UOM Categroy"
    _order = "name"

    name = fields.Char("Name", required=True)
    type_id = fields.Many2one("pms.uom.category", "Type")

    _sql_constraints = [('name_unique', 'unique(name)',
                         'Your name is exiting in the database.')]


class PMSBank(models.Model):
    _name = 'pms.bank'
    _description = "Bank"

    country = fields.Many2one("pms.country", "Country Name")
    city_id = fields.Many2one("pms.city", "City Name")
    state_id = fields.Many2one("pms.state", "State Name")
    name = fields.Char("Name")
    bic = fields.Char("Bank Identifier Code")
    phone = fields.Char("Phone")
    email = fields.Char("Email")
    no = fields.Char("No")
    street = fields.Char("Street")
    zip_code = fields.Char("Zip")
    active = fields.Char(default=True)


class Bank(models.Model):
    _inherit = 'res.bank'

    bic = fields.Char('Switch Code',
                      index=True,
                      help="Sometimes called BIC or Swift.")
    branch = fields.Char("Branch Name",
                         index=True,
                         help="Sometimes called BIC or Swift.")
    city_id = fields.Many2one("pms.city", "City Name", ondelete='cascade')
    township = fields.Many2one("pms.township", "Township")

    _sql_constraints = [('name_unique', 'unique(name)',
                         'Your name is exiting in the database.')]


class PMSCity(models.Model):
    _name = "pms.city"
    _description = "City"
    _order = "code,name"

    state_id = fields.Many2one("res.country.state",
                               "State Name",
                               required=True)
    name = fields.Char("City Name", required=True)
    code = fields.Char("City Code", required=True)


class Company(models.Model):
    _inherit = "res.company"
    _description = 'Companies'
    _order = 'sequence, name'

    city_id = fields.Many2one("pms.city",
                              "City Name",
                              compute='_compute_address',
                              inverse='_inverse_city',
                              ondelete='cascade')
    township = fields.Many2one("pms.township",
                               "Township Name",
                               compute='_compute_address',
                               inverse='_inverse_township',
                               ondelete='cascade')
    company_type = fields.Many2one('pms.company.category', "Company Type")
    partner_contact_id = fields.Many2many(
        "res.partner",
        "company_partner_contact_rel",
        "company_id",
        "partner_id",
        domain="[('is_company', '!=', True)]",
        store=True)

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

    name = fields.Char("Name", required=True)
    code = fields.Char("Code", required=True)
    city_id = fields.Many2one("pms.city",
                              "City",
                              ondelete='cascade',
                              required=True)


class PMSState(models.Model):
    _name = "pms.state"
    _description = "State"

    country_id = fields.Many2one("pms.country", "Country Name", required=True)
    name = fields.Char("State Name", required=True)
    code = fields.Char("State Code", required=True)


class PMSCountry(models.Model):
    _name = "pms.country"
    _description = "Country"

    name = fields.Char("Country Name", required=True)
    code = fields.Char("Country Code", required=True)


class PMSCurrency(models.Model):
    _name = "pms.currency"
    _description = "Currency"

    name = fields.Char("Name", required=True)
    symbol = fields.Char("Symbol", required=True)
    status = fields.Boolean("Active")

    @api.multi
    def action_status(self):
        if self.status == True:
            self.status = False
        else:
            self.status = True


class PMSCompany(models.Model):
    _name = "pms.company"
    _description = "Company"

    name = fields.Char("Name", required=True)


class PMSDepartment(models.Model):
    _name = "pms.department"
    _description = "Department"
    _order = "name"

    name = fields.Char("Name", required=True)
    parent_id = fields.Many2one("pms.department", "Parent Department")


class PMSPosition(models.Model):
    _name = "pms.position"
    _description = "Positions"
    _order = "name"

    name = fields.Char("Name", required=True)
    parent_id = fields.Many2one("pms.department", "Parent Department")


class PMSCompanyCategory(models.Model):
    _name = "pms.company.category"
    _description = "Company Categorys"

    name = fields.Char("Description", required=True)
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        for ct in self:
            if not ct.active:
                ct.active = self.active
        super(PMSCompanyCategory, self).toggle_active()


class Partner(models.Model):
    _inherit = "res.partner"

    city_id = fields.Many2one("pms.city", "City Name", ondelete='cascade')
    credit_card_id = fields.Many2one("pms.credit_card", "Credit Cards")
    categ_id = fields.Many2one("pms.category", "Categorys")
    categss_id = fields.Many2one("pms.category", "Cate")
    post_id = fields.Many2one("pms.position", "Position")
    company_type = fields.Selection(
        string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company')],
        compute='_compute_company_type',
        inverse='_write_company_type',
    )
    type = fields.Selection(
        [
            ('contact', 'Contact'),
            ('invoice', 'Invoice address'),
            ('other', 'Other address'),
        ],
        string='Address Type',
        default='contact',
        help=
        "Used by Sales and Purchase Apps to select the relevant address depending on the context."
    )
    child_ids = fields.One2many('res.partner',
                                'parent_id',
                                string='Contacts',
                                domain=[('is_company', '!=', True)])
    compnay_channel_type = fields.Many2many('pms.company.category',
                                            string="Type")
    township = fields.Many2one('pms.township', "Township", ondelete='cascade')

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


class PMSCreditCard(models.Model):
    _name = "pms.credit_card"

    name = fields.Char("Name")


class PMSCategory(models.Model):
    _name = "pms.category"
    _description = "Categorys"

    name = fields.Char("Description", required=True)

    # dis_company_type = fields.Boolean("Disable")
    # department_id = fields.Many2one(
    #     "pms.department",
    #     "Department",
    #     help="Department is set the partner department.")


# class PMSPartner(models.Model):
#     _name = "pms.partner"
#     _order = "name"

#     country_id = fields.Many2one("pms.country", "Country Name")
#
#     state_id = fields.Many2one("pms.state", "State Name")
#     name = fields.Char("Name", required=True)
#     email = fields.Char("Email",
#                         help='Format email address "Name <email@domain>"')
#     phone = fields.Char("Phone")
#     mobile = fields.Char("Mobile")
#     bank_id = fields.Many2one("pms.bank", "Bank Name")
#     is_company = fields.Boolean(
#         string='Is a Company',
#         default=False,
#         help="Check if the contact is a company, otherwise it is a person")
#     parent_id = fields.Many2one("pms.partner", "Parent", index=True)
#     child_ids = fields.One2many('pms.partner',
#                                 'parent_id',
#                                 string='Contacts',
#                                 domain=[('active', '=', True)])
#     company_id = fields.Many2one("pms.partner", "Company", index=True)
#     company_type = fields.Selection(string='Company Type',
#                                     selection=[('person', 'Individual'),
#                                                ('company', 'Company')],
#                                     default="person")
#     vat = fields.Char(
#         string='Tax ID',
#         help=
#         "The Tax Identification Number. Complete it if the contact is subjected to government taxes. Used in some legal statements."
#     )
#     website = fields.Char()
#     customer = fields.Boolean(
#         string='Is a Customer',
#         default=True,
#         help=
#         "Check this box if this contact is a customer. It can be selected in sales orders."
#     )
#     function = fields.Char(string='Job Position')
#     # job_id = fields.Many2one("pms.job", string="Job Position")
#     street = fields.Char()
#     street2 = fields.Char()
#     comment = fields.Text()
#     zip = fields.Char(change_default=True)
#     active = fields.Boolean(default=True)
#     address_type = fields.Selection(
#         [
#             ('contact', 'Contact'),
#             ('invoice', 'Invoice address'),
#             ('other', 'Other address'),
#         ],
#         string='Address Type',
#         default='contact',
#         help=
#         "Used by contact,invoice and other address Apps to select the relevant address depending on the context."
#     )
#     image = fields.Binary(
#         "Image",
#         attachment=True,
#         help=
#         "This field holds the image used as avatar for this contact, limited to 1024x1024px",
#     )
#     image_medium = fields.Binary("Medium-sized image", attachment=True, help="Medium-sized image of this contact. It is automatically "\
#         "resized as a 128x128px image, with aspect ratio preserved. "\
#         "Use this field in form views or some kanban views.")
#     image_small = fields.Binary("Small-sized image", attachment=True, help="Small-sized image of this contact. It is automatically "\
#         "resized as a 64x64px image, with aspect ratio preserved. "\
#         "Use this field anywhere a small image is required.")
#     color = fields.Integer(string='Color Index', default=0)
#     company_street = fields.Char("Street",
#                                  related="company_id.street",
#                                  store=False)
#     company_street2 = fields.Char("Street2",
#                                   related="company_id.street2",
#                                   store=False)
#     company_city = fields.Many2one("pms.city",
#                                    "City",
#                                    related="company_id.city",
#                                    store=False)
#     company_state_id = fields.Many2one("pms.state",
#                                        "State",
#                                        related="company_id.state_id",
#                                        store=False)
#     company_zip = fields.Char("Zip", related="company_id.zip", store=False)
#     company_country_id = fields.Many2one("pms.country",
#                                          "Country",
#                                          related="company_id.country_id",
#                                          store=False)
#     company_country_vat = fields.Char(
#         string='Tax ID',
#         related="company_id.vat",
#         store=False,
#         help=
#         "The Tax Identification Number. Complete it if the contact is subjected to government taxes. Used in some legal statements."
#     )
#     department_id = fields.Many2one(
#         "pms.department",
#         "Department",
#         help="Department is set the partner department.")

#     @api.onchange('company_type')
#     def onchange_company_type(self):
#         for partner in self:
#             if partner.company_type == 'company':
#                 partner.customer = False
#                 partner.is_company = True
#                 partner.company_id = False
#             else:
#                 partner.customer = True
#                 partner.is_company = False
#                 partner.parent_id = False

#     # @api.onchange('company_id')
#     # def onchange_company_id(self):
#     #     #default address from company of user will calculate in this funcition
#     #     for company in self:
#     #         if not company.company_id:
#     #             company.street = False
#     #             company.street2 = False
#     #             company.city = False
#     #             company.state_id = False
#     #             company.country_id = False
#     #         else:
#     #             company.street = company.company_id.street
#     #             company.street2 = company.company_id.street2
#     #             company.city = company.company_id.city
#     #             company.state_id = company.company_id.state_id
#     #             company.country_id = company.company_id.country_id

#     @api.model
#     def create(self, values):
#         if values['image']:
#             tools.image_resize_images(values, sizes={'image': (1024, None)})
#         if values['company_id'] and values['company_type'] == 'person':
#             company_id = self.env['pms.partner'].browse(values['company_id'])
#             values['street'] = company_id.street
#             values['street2'] = company_id.street2
#             values['city'] = company_id.city.id
#             values['state_id'] = company_id.state_id.id
#             values['country_id'] = company_id.country_id.id
#             values['vat'] = company_id.vat
#         return super(PMSPartner, self).create(values)

#     @api.multi
#     def write(self, vals):
#         tools.image_resize_images(vals, sizes={'image': (1024, None)})
#         return super(PMSPartner, self).write(vals)
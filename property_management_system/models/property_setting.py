# -*- coding: utf-8 -*-
import json
import calendar
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from odoo.addons.property_management_system.models import api_rauth_config


class PMSRentSchedule(models.Model):
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

    state = fields.Selection([('draft', "Draft"), ('generated', "Generated"),
                              ('pre-terminated', "Pre-Terminated")],
                             "Status",
                             default="draft")
    billing_date = fields.Date(string="Billing Date", required=True)
    active = fields.Boolean(default=True)
    is_api_post = fields.Boolean("Posted")

    @api.multi
    def action_generate_rs(self):
        val = {}
        dpos_obj = self.env['pos.daily.sale']
        for line in self:
            total_amount = 0
            cct_name = ccm_name = None
            lsd_year = line.end_date.year
            lsd_month = line.end_date.month
            if line.state == 'draft':
                for charge in line.charge_type:
                    net_amount = 0
                    cct_name = charge.charge_type_id.name
                    ccm_name = charge.calculation_method_id.name
                    for lagl in line.lease_agreement_line_id:
                        total_rate = total_unit = 0
                        pct_name = pcm_name = laptl_ids = None
                        laptl_ids = lagl.applicable_type_line_id
                        for apl in laptl_ids:
                            pct_name = apl.charge_type_id.name
                            pcm_name = apl.calculation_method_id.name
                            apc_id = apl.applicable_charge_id
                            st_name = apc_id.source_type_id.name
                            cst_name = charge.source_type_id.name
                            meter_amount = 0
                            if cct_name == 'Rental':
                                if ccm_name == 'Fix':
                                    if pct_name == cct_name and apl.start_date <= line.start_date and apl.end_date >= line.end_date and pcm_name == ccm_name:
                                        total_rate = apl.rate
                                elif ccm_name == 'Area':
                                    total_rate = line.amount
                                elif ccm_name == 'Percentage':
                                    percent_amount = 0
                                    if pcm_name == ccm_name:
                                        if lagl.leaseunitpos_line_id:
                                            lpl_ids = lagl.leaseunitpos_line_id
                                            for lid in lpl_ids:
                                                pos_id = dpos_obj.search([
                                                    ('pos_interface_code', '=',
                                                     lid.posinterfacecode_id.
                                                     name),
                                                    ('pos_receipt_date', '>=',
                                                     line.start_date),
                                                    ('pos_receipt_date', '<=',
                                                     line.end_date)
                                                ])
                                                if pos_id:
                                                    for daily in pos_id:
                                                        net_amount += daily.grosssalesamount
                                            percent_amount = apl.rate
                                            total_rate = (net_amount *
                                                          percent_amount) / 100
                                else:
                                    total_rate = 0
                            if cct_name == 'Service':
                                if ccm_name == 'Fix':
                                    if pct_name == cct_name and apl.start_date <= line.start_date and apl.end_date >= line.end_date and pcm_name == ccm_name:
                                        total_rate = apl.rate
                                else:
                                    total_rate = 0
                            if cct_name == 'Utilities':
                                if ccm_name == 'MeterUnit':
                                    if lagl.unit_no.facility_line:
                                        luf_lines = lagl.unit_no.facility_line
                                        for fl in luf_lines:
                                            if fl.facilities_line:
                                                umon_obj = self.env[
                                                    'pms.utilities.monthly']
                                                filter_month = str(lsd_year) + (
                                                    ('0' + str(lsd_month))
                                                    if len(str(lsd_month)) <= 1
                                                    else str(lsd_month))
                                                meter_code = line.charge_type.source_type_id.code
                                                monthly_id = umon_obj.search([
                                                    ('utilities_source_type',
                                                     '=', meter_code),
                                                    ('utilities_no', '=',
                                                     fl.utilities_no.name),
                                                    ('utilities_supply_type',
                                                     '=',
                                                     fl.utilities_type_id.code
                                                     ),
                                                    ('billingperiod', '=',
                                                     filter_month)
                                                ])
                                                if monthly_id:
                                                    meter_amount = monthly_id.end_value - monthly_id.start_value
                                    if st_name == cst_name and pct_name == cct_name and apl.start_date <= line.start_date and apl.end_date >= line.end_date and pcm_name == ccm_name:
                                        if charge.use_formula == False:
                                            amount = apl.rate
                                            total_unit = meter_amount * amount
                                        else:
                                            if charge.unit_charge_line:
                                                for ucl in charge.unit_charge_line:
                                                    if meter_amount > ucl.from_unit and meter_amount < ucl.to_unit:
                                                        total_unit += (
                                                            meter_amount -
                                                            ucl.from_unit -
                                                            1) * ucl.rate
                                                    elif meter_amount > ucl.from_unit and meter_amount > ucl.to_unit:
                                                        total_unit += (
                                                            ucl.to_unit -
                                                            (ucl.from_unit +
                                                             1)) * ucl.rate
                                                    else:
                                                        total_unit += total_unit
                                else:
                                    total_unit = 0
                            if total_rate and not total_unit:
                                total_amount = total_rate
                            elif total_unit and not total_rate:
                                total_amount = total_unit
                            else:
                                total_amount = total_amount
                schedule_invoice = line.lease_no + "/" + line.unit_no.name + "/" + str(
                    line.id)
                val = {
                    'name': line.name,
                    'property_id': line.property_id.id,
                    'lease_agreement_id': line.lease_agreement_id.id,
                    'start_date': line.start_date,
                    'end_date': line.end_date,
                    'amount': total_amount,
                    'charge_type': line.charge_type.id,
                    'lease_no': line.lease_no,
                    'state': line.state,
                    'unit_no': line.unit_no.id,
                    'billing_date': line.billing_date,
                    'schedule_invoice': schedule_invoice,
                }
                gen_ids = self.env['pms.gen.rent.schedule'].search([
                    ('schedule_invoice', '=', schedule_invoice)
                ])
                if gen_ids:
                    gen_id = gen_ids.write(val)
                else:
                    gen_id = self.env['pms.gen.rent.schedule'].create(val)
                if gen_id:
                    line.write({'state': 'generated', 'amount': total_amount})

    def action_reset_draft(self):
        if self.state == 'generated':
            self.write({'state': 'draft'})

    def action_reset_drafts(self):
        if self:
            for rent in self:
                rent.action_reset_draft()

    def rent_schedule_schedular(self):
        values = None
        property_id = None
        property_ids = self.env['pms.properties'].search([
            ('api_integration', '=', True), ('api_integration_id', '!=', False)
        ])
        for pro in property_ids:
            property_id = pro
            lease_ids = self.search([('is_api_post', '=', False),
                                    ('property_id', '=', property_id.id)])
            for lease in lease_ids.lease_agrrement_line:
                for chline in lease.applicable_type_line_id:
                    if chline.applicable_charge_id.charge_type_id:
                        exported = chline.applicable_charge_id.charge_type_id.is_export
                        if exported:
                            integ_obj = property_id.api_integration_id
                            integ_line_obj = integ_obj.api_integration_line
                            api_line_ids = integ_line_obj.search([
                                ('name', '=', "RentSchedule")
                            ])
                            datas = api_rauth_config.APIData.get_data(lease, values,
                                                                    property_id, integ_obj,
                                                                    api_line_ids)
                            if datas:
                                if datas.res:
                                    response = json.loads(datas.res)
                                    if 'responseStatus' in response:
                                        if response['responseStatus']:
                                            if 'message' in response:
                                                if response['message'] == 'SUCCESS':
                                                    for lid in lease_ids:
                                                        lid.write({'is_api_post': True})

    @api.multi
    def toggle_active(self):
        for pt in self:
            if not pt.active:
                pt.active = self.active
        super(PMSRentSchedule, self).toggle_active()

    @api.model
    def create(self, values):
        rentschedule_id = self.search([
            ('property_id', '=', values['property_id']),
            ('unit_no', '=', values['unit_no']),
            ('lease_no', '=', values['lease_no']),
            ('lease_agreement_line_id', '=',
             values['lease_agreement_line_id']),
            ('charge_type', '=', values['charge_type']),
            ('start_date', '=', values['start_date']),
            ('end_date', '=', values['end_date']),
            ('active', '=', True),
        ])
        if rentschedule_id:
            raise UserError(_("Rent Schedular is already existed."))
        return super(PMSRentSchedule, self).create(values)


class PMSPropertyType(models.Model):
    _name = 'pms.property.type'
    _description = 'Property Types'
    _order = 'sequence, name'

    name = fields.Char("Property Type", required=True, track_visibility=True)
    description = fields.Text("Description", track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)
    sequence = fields.Integer(track_visibility=True)
    index = fields.Integer(compute='_compute_index')

    _sql_constraints = [('name_unique', 'unique(name)',
                         'Your name is exiting in the database.')]
    
    @api.one
    def _compute_index(self):
        cr, uid, ctx = self.env.args
        self.index = self._model.search_count(cr,uid,[('sequence','<',self.sequence)],context=ctx) + 1

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


class PMSUtilitiesSupply(models.Model):
    _name = "pms.utilities.supply"
    _description = "Utilities Supply"
    _order = "sequence,name"

    name = fields.Char("Utilities supply",
                       required=True,
                       track_visibility=True)
    code = fields.Char("Utilities Supply Code",
                       required=True,
                       track_visibility=True)
    utilities_type_id = fields.Many2one('pms.utilities.type',
                                        "Utilities Type",
                                        required=True,
                                        track_visibility=True)
    export_supply_type = fields.Char("Export Supply Type")
    description = fields.Text("Description",track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)
    sequence = fields.Integer(track_visibility=True)
    index = fields.Integer(compute='_compute_index')
    
    @api.one
    def _compute_index(self):
        cr, uid, ctx = self.env.args
        self.index = self._model.search_count(cr,uid,[('sequence','<',self.sequence)],context=ctx) + 1

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
        super(PMSUtilitiesSupply, self).toggle_active()

    @api.model
    def create(self, values):
        soruc_id = self.search([('code', '=', values['code'])])
        if soruc_id:
            raise UserError(_("%s is already existed" % values['code']))
        return super(PMSUtilitiesSupply, self).create(values)

    @api.multi
    def write(self, vals):
        if 'code' in vals:
            soruc_id = self.search([('code', '=', vals['code'])])
            if soruc_id:
                raise UserError(_("%s is already existed" % vals['code']))
        return super(PMSUtilitiesSupply, self).write(vals)


class PMSUtilitiesType(models.Model):
    _name = "pms.utilities.type"
    _description = "Utilities Type"
    _order = 'sequence,name'

    name = fields.Char("Utilities Type",
                       required=True,
                       track_visibility=True)
    code = fields.Char("Utilities Type Code",
                       required=True,
                       track_visibility=True)
    export_utilities_type = fields.Char("Export Utilities Type")
    description = fields.Text("Description", track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)
    sequence = fields.Integer(track_visibility=True)
    index = fields.Integer(compute='_compute_index')
    _sql_constraints = [('code_unique', 'unique(code)',
                         'Code is already existed.')]

    @api.one
    def _compute_index(self):
        cr, uid, ctx = self.env.args
        self.index = self._model.search_count(cr,uid,[('sequence','<',self.sequence)],context=ctx) + 1

    # @api.multi
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         code = record.code
    #         result.append((record.id, code))
    #     return result

    @api.multi
    def toggle_active(self):
        for pt in self:
            if not pt.active:
                pt.active = self.active
        super(PMSUtilitiesType, self).toggle_active()


class PMSFacilitiesline(models.Model):
    _name = 'pms.facility.lines'
    _description = "Facility Lines"

    def get_property_id(self):
        if self._context.get('property_id') != False:
            return self._context.get('property_id')
    def get_start_date(self):
        if self.facility_id.install_date:
            self.start_date = self.facility_id.install_date

    facility_id = fields.Many2one("pms.facilities",
                                  "Facilities",
                                  track_visibility=True)
    source_type_id = fields.Many2one('pms.utilities.supply',
                                     "Utilities Supply",
                                     required=True,
                                     track_visibility=True)
    start_date = fields.Date("Start Date", default=get_start_date, track_visibility=True)
    initial_value = fields.Float("Initial Value", track_visibility=True)
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
            utilities_ids = self.env['pms.utilities.supply'].search([
                ('utilities_type_id', '=',
                 self.facility_id.utilities_type_id.id)
            ])
            for uti in utilities_ids:
                uti_ids.append(uti.id)
            domain = {'source_type_id': [('id', 'in', uti_ids)]}
        return {'domain': domain}
    

    @api.multi
    @api.onchange('end_date','facility_id')
    def onchange_end_date(self):
        facility_line_id = self._origin.id
        if self.end_date:
            space_fline_id = self.env['pms.space.unit.facility.lines'].search([('facility_line_id','=',facility_line_id),('inuse','=',True)])
            space_fline_id.write({'end_date': self.end_date, 'inuse':False})
            self.active = False


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
    # space_unit_code_len = fields.Integer("Space Unit Code Len",
    #                                      track_visibility=True)
    active = fields.Boolean("Active", default=True, track_visibility=True)

    @api.multi
    def toggle_active(self):
        for pt in self:
            if not pt.active:
                pt.active = self.active
        super(PMSTerms, self).toggle_active()

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
                         
    township = fields.Many2one("pms.township",
                               "Township",
                               store=True,
                               track_visibility=True)
    city_id = fields.Many2one("pms.city",
                              "City Name",
                              readonly=False,
                              related="township.city_id",
                              store=True,
                              track_visibility=True,
                              ondelete='cascade')
    state_id = fields.Many2one("res.country.state",
                               "State Name",
                               readonly=False,
                               related="city_id.state_id",
                               store=True,
                               track_visibility=True)
    country_id = fields.Many2one('res.country',
                                 string='Country Name',
                                 readonly=False,
                                 related="state_id.country_id",
                                 track_visibility=True,
                                 ondelete='restrict')

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
    _sql_constraints = [('code_unique', 'unique(code)',
                         'City Code is already existed.')]


class Company(models.Model):
    _inherit = "res.company"
    _description = 'Companies'
    _order = 'sequence, name'

    city_id = fields.Many2one("pms.city",
                              "City Name",
                              compute='_compute_address',
                              inverse='_inverse_city',
                              related="township.city_id",
                              readonly=False,
                              track_visibility=True,
                              ondelete='cascade')
    township = fields.Many2one("pms.township",
                               "Township Name",
                               compute='_compute_address',
                               inverse='_inverse_township',
                               track_visibility=True,
                               ondelete='cascade')
    state_id = fields.Many2one("res.country.state",
                               string='State',
                               related="city_id.state_id",
                               ondelete='restrict',
                               track_visibility=True,
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country',
                                 string='Country',
                                 readonly=False,
                                 related="state_id.country_id",
                                 requried=True,
                                 track_visibility=True,
                                 ondelete='restrict')
    company_type = fields.Many2many('pms.company.category',
                                    "res_company_type_rel",
                                    'company_id',
                                    'category_id',
                                    track_visibility=True)

    _sql_constraints = [('name_unique', 'unique(name)',
                         'Your name is exiting in the database.')]

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
    _sql_constraints = [('code_unique', 'unique(code)',
                         'Township Code is already existed.')]


class PMSCountry(models.Model):
    _name = "pms.country"
    _description = "Country"

    name = fields.Char("Country Name", required=True, track_visibility=True)
    code = fields.Char("Country Code", required=True, track_visibility=True)
    _sql_constraints = [('code_unique', 'unique(code)',
                         'Country Code is already existed.')]


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
    _order = 'sequence,code,name'

    name = fields.Char("Description", required=True, track_visibility=True)
    code = fields.Char("Code", track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)
    sequence = fields.Integer(track_visibility=True)
    index = fields.Integer(compute='_compute_index')

    @api.one
    def _compute_index(self):
        cr, uid, ctx = self.env.args
        self.index = self._model.search_count(cr,uid,[('sequence','<',self.sequence)],context=ctx) + 1

    @api.multi
    def toggle_active(self):
        for ct in self:
            if not ct.active:
                ct.active = self.active
        super(PMSCompanyCategory, self).toggle_active()


class Partner(models.Model):
    _inherit = "res.partner"

    # def _default_property(self):
    #     return self.env['pms.properties']._property_default_get('res.partner')


    company_type = fields.Selection(
        string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company')],
        compute='_compute_company_type',
        inverse='_write_company_type',
        track_visibility=True,
    )
    child_ids = fields.One2many('res.partner',
                                'parent_id',
                                string='Contacts',
                                track_visibility=True,
                                domain=[('is_company', '!=', True)])
    company_channel_type = fields.Many2many('pms.company.category',
                                            string="CRM Type",
                                            track_visibility=True)
    township = fields.Many2one('pms.township',
                               "Township", ondelete='restrict', track_visibility=True)
    city_id = fields.Many2one("pms.city", "City Name", ondelete='restrict', related="township.city_id", readonly=False, store=True, track_visibility=True)
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',related="city_id.state_id", readonly=False, store=True, domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', related="state_id.country_id", readonly=False, store=True, ondelete='restrict')
    is_tanent = fields.Boolean('Is Tanent',
                               compute="get_tanent",
                               readonly=False,
                               store=True,
                               track_visibility=True)
    trade_id = fields.Many2one("pms.trade_category",
                               "Trade",
                               track_visibility=True)
    sub_trade_id = fields.Many2one("pms.sub_trade_category",
                                   "Sub Trade",
                                   track_visibility=True)
    is_api_post = fields.Boolean("Posted")
    is_company = fields.Boolean(string='Is a Company', default=True, help="Check if the contact is a company, otherwise it is a person")
    is_shop = fields.Boolean(string='Is a shop', help="Check if the contact is a company or branch, otherwise it is a person")
    shop_ids = fields.One2many('res.partner', "parent_id", string='Shop', domain=[('is_shop', '=', True)], track_visibility=True, index=True)
    lease_id = fields.Many2one("pms.lease_agreement", "Lease")
    lease_line_id = fields.Many2one("pms.lease_agreement.line", "Lease Line")
    current_property_id = fields.Many2one("pms.properties", string="Properties")

    


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
        if not self.company_channel_type:
            if 'default_code' in self.company_channel_type._context:
                if self.company_channel_type._context.get('default_code') in ('TENANT','NON-TENANT'):
                    code = self.company_channel_type._context.get('default_code')
                    self.company_channel_type = self.company_channel_type.search([('code','=',code)])
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


    def crm_scheduler(self):
        values = None
        property_id = None
        partner_id = []

        partner_ids = self.env['res.company'].search([])
        for cpid in partner_ids:
            partner_id.append(cpid.partner_id.id)
        crmaccount_ids = self.search([('is_api_post', '=', False),
                                      ('is_company', '=', True),
                                      ('company_channel_type', '!=', False),
                                      ('id', 'not in', partner_id)])
        if crmaccount_ids:
            integ_obj = self.env['pms.api.integration'].search([])
            api_line_ids = self.env['pms.api.integration.line'].search([
                ('name', '=', "CRMAccount")
            ])
            datas = api_rauth_config.APIData.get_data(crmaccount_ids, values,
                                                      property_id, integ_obj,
                                                      api_line_ids)
            if datas:
                if datas.res:
                    response = json.loads(datas.res)
                    if 'responseStatus' in response:
                        if response['responseStatus']:
                            if 'message' in response:
                                if response['message'] == 'SUCCESS':
                                    for ca in crmaccount_ids:
                                        ca.update({'is_api_post': True})

    @api.model
    def create(self, values):
        if 'name' in values:
            crm_id = self.search([('name', '=', values['name']),
                                  ('is_company', '=', True)])
            if crm_id:
                raise UserError(_("%s is already existed" % values['name']))
        return super(Partner, self).create(values)

    @api.one
    def write(self, vals):
        if 'name' in vals:
            crm_id = self.env['res.partner'].search([
                ('name', '=', vals['name']), ('is_company', '=', True)
            ])
            if crm_id:
                for crm in crm_id:
                    if crm.name != self.name:
                        raise UserError(
                            _("%s is already existed" % vals['name']))
        id = None
        id = super(Partner, self).write(vals)
        if self.is_company and self.company_channel_type:
            if 'is_api_post' not in vals:
                property_id = None
                integ_obj = self.env['pms.api.integration'].search([])
                api_line_ids = self.env['pms.api.integration.line'].search([
                    ('name', '=', "CRMAccount")
                ])
                datas = api_rauth_config.APIData.get_data(self, vals, property_id, integ_obj, api_line_ids)
                if datas:
                    if 'res' in datas:
                        if datas.res:
                            response = json.loads(datas.res)
                            if 'responseStatus' in response:
                                if response['responseStatus']:
                                    if 'message' in response:
                                        if response['message'] == 'SUCCESS':
                                            self.write({'is_api_post': True})
        return id

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        chosen_name = default.get('name') if default else ''
        if self.name:
            crm_id = self.search([('name', '=', self.name)])
            if crm_id:
                raise UserError(_("%s is already existed" % self.name))
        new_name = chosen_name or _('%s (copy)') % self.name
        default = dict(default or {}, name=new_name)
        return super(Partner, self).copy(default)


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
                             default="draft",
                             track_visibility=True)
    billing_date = fields.Date(string="Billing Date", required=True)
    schedule_invoice = fields.Char("Schedule Invoice")

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
        invoice_month = unit = inv_ids = None
        lease = []
        for ls in self:
            invoice_lines = []
            if ls.state == 'confirmed':
                invoice_month = str(
                    calendar.month_name[ls.billing_date.month]) + ' - ' + str(
                        ls.billing_date.year)
                for line in self:
                    product_name = None
                    if line.property_id == ls.property_id and line.billing_date == ls.billing_date and line.lease_no == ls.lease_no:
                        product_name = line.charge_type.name
                        prod_ids = self.env['product.template'].search([
                            ('name', 'ilike', product_name)
                        ])
                        prod_id = self.env['product.product'].search([
                            ('product_tmpl_id', '=', prod_ids.id)
                        ])
                        if not prod_ids:
                            val = {
                                'name': product_name,
                                'sale_ok': False,
                                'is_unit': True
                            }
                            product_tmp_id = self.env[
                                'product.template'].create(val)
                            product_tmp_ids = self.env[
                                'product.product'].search([
                                    ('product_tmpl_id', '=', product_tmp_id.id)
                                ])
                            if not product_tmp_ids:
                                product_id = self.env[
                                    'product.product'].create(
                                        {'product_tmpl_id': product_tmp_id.id})
                            product_id = product_tmp_ids or product_id
                        else:
                            product_id = prod_id
                        account_id = False
                        account_id = product_id.property_account_income_id.id or product_id.categ_id.property_account_income_categ_id.id
                        taxes = product_id.taxes_id.filtered(
                            lambda r: not line.lease_agreement_id.company_id or
                            r.company_id == line.lease_agreement_id.company_id)
                        unit = line.unit_no
                        inv_line_id = self.env['account.invoice.line'].create({
                            'name':
                            _(product_name),
                            'unit_no':unit.id,
                            'charge_type_id': line.charge_type.charge_type_id.id,
                            'account_id':
                            account_id,
                            'price_unit':
                            line.amount,
                            'quantity':
                            1,
                            'uom_id':
                            product_id.uom_id.id,
                            'product_id':
                            product_id.id,
                            'invoice_line_tax_ids': [(6, 0, taxes.ids)],
                        })
                        invoice_lines.append(inv_line_id.id)
                        line.write({'state': 'invoiced'})
                inv_ids = self.env['account.invoice'].create({
                    'lease_items':
                    ls.name,
                    'lease_no':
                    ls.lease_agreement_id.lease_no,
                    'inv_month':
                    invoice_month,
                    'partner_id':
                    ls.lease_agreement_id.company_tanent_id.id,
                    'property_id':
                    ls.lease_agreement_id.property_id.id,
                    'company_id':
                    ls.lease_agreement_id.company_id.id,
                    'invoice_line_ids': [(6, 0, invoice_lines)],
                })
        return True

import json
import pytz
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.addons.property_management_system.models import api_rauth_config

_tzs = [
    (tz, tz)
    for tz in sorted(pytz.all_timezones,
                     key=lambda tz: tz if not tz.startswith('Etc/') else '_')
]


def _tz_get(self):
    return _tzs


class PMSProperties(models.Model):
    _name = 'pms.properties'
    _inherit = ['mail.thread']
    _description = 'Property Management System'
    _order = "code"

    def _default_propertytype(self):
        pro_type = None
        if not self.propertytype_id:
            pro_type = self.env["pms.property.type"].search([('name','=',"Retail")]) or self.env["pms.property.type"].search([])
            if len(pro_type)>1:
                pro_type = pro_type[0]
        return pro_type

    def _default_uom_id(self):
        uom_ids = None
        if not self.uom_id:
            categ_ids = self.env[('uom.category')].search([('name','=','Area')]).id
            uom_ids = self.env["uom.uom"].search([('name','=',"sqft"),('category_id','=',categ_ids)]) or self.env["uom.uom"].search([])
            if len(uom_ids)>1:
                uom_ids = uom_ids[0]
        return uom_ids

    def default_get_curency(self):
        mmk_currency_id = self.env['res.currency'].search([('name', '=', 'MMK')
                                                           ])
        usd_currency_id = self.env['res.currency'].search([('name', '=', 'USD')
                                                           ])
        if mmk_currency_id.active is False:
            return usd_currency_id
        else:
            return mmk_currency_id

    def default_get_country(self):
        country_id = None
        if self.currency_id:
            country_id = self.env['res.country'].search([
                ('currency_id', '=', self.currency_id.id)
            ])
        else:
            country_id = self.env['res.country'].search([('code', '=', "MM")])
        return country_id
    
    propertytype_id = fields.Many2one(
        "pms.property.type",
        "Property Type",
        required=True,
        track_visibility=True,
        default =_default_propertytype,
        help="The properties's type is set the specific type.")
    uom_id = fields.Many2one("uom.uom",
                             "UOM",
                             required=True,
                             domain=[('category_id.name', '=', 'Area')],
                             track_visibility=True,
                             default=_default_uom_id,
                             help="Unit Of Measure is need to set for Area.")
    bank_id = fields.Many2one('res.bank',
                              "Bank Information",
                              track_visibility=True)
    township = fields.Many2one("pms.township",
                               string='Township',
                               ondelete='restrict',
                               track_visibility=True,
                               domain="[('city_id', '=?', city_id)]")
    city_id = fields.Many2one("pms.city",
                              string='City',
                              related="township.city_id",
                              ondelete='restrict',
                              track_visibility=True,
                              domain="[('state_id', '=?', state_id)]")
    state_id = fields.Many2one("res.country.state",
                               string='State',
                               related="city_id.state_id",
                               ondelete='restrict',
                               track_visibility=True,
                               domain="[('country_id', '=?', country_id)]")
    currency_id = fields.Many2one("res.currency",
                                  "Currency",
                                  default=default_get_curency,
                                  readonly=False,
                                  track_visibility=True,
                                  store=True)
    country_id = fields.Many2one('res.country',
                                 string='Country',
                                 default=default_get_country,
                                 readonly=False,
                                 related="state_id.country_id",
                                 requried=True,
                                 track_visibility=True,
                                 ondelete='restrict')
    name = fields.Char("Name", required=True, size=250, track_visibility=True)
    code = fields.Char("Code", size=250, required=True, track_visibility=True)
    gross_floor_area = fields.Float('GFA',
                                    digits=(16, 2),
                                    help="Gross Floor Area",
                                    track_visibility=True)
    net_lett_able_area = fields.Float('NLA',
                                      digits=(16, 2),
                                      help="Net Lett-able Area",
                                      track_visibility=True)
    web_site_url = fields.Char("Website",
                               size=250,
                               help="Website URL",
                               track_visibility=True)
    is_autogenerate_posid = fields.Boolean("Auto Generate Pos ID",
                                           help="Auto Generating POS ID?",
                                           track_visibility=True)
    project_start_date = fields.Date("Project Start Date",
                                     track_visibility=True)
    target_open_date = fields.Date("Target Opening Date",
                                   track_visibility=True)
    actual_opening_date = fields.Date("Actual Openiing Date",
                                      track_visibility=True)
    timezone = fields.Selection(
        _tz_get,
        string='Timezone',
        default=lambda self: self._context.get('tz'),
        track_visibility=True,
        help=
        "The partner's timezone, used to output proper date and time values "
        "inside printed reports. It is important to set a value for this field. "
        "You should use the same timezone that is otherwise used to pick and "
        "render date and time values: your computer's timezone.")
    no = fields.Char(track_visibility=True)
    street = fields.Char(track_visibility=True)
    zip = fields.Char(change_default=True, track_visibility=True)
    property_contact_id = fields.Many2many(
        'res.partner',
        'pms_property_contact_rel',
        'property_id',
        'partner_id',
        string='Contacts',
        track_visibility=True,
        domain="[('is_company', '!=', True)]")
    property_management_id = fields.Many2many('res.company',
                                              'pms_property_managements_rel',
                                              'property_id',
                                              'partner_id',
                                              track_visibility=True,
                                              string='Managements')
    image = fields.Binary(
        "Image",
        attachment=True,
        track_visibility=True,
        help=
        "This field holds the image used as avatar for this contact, limited to 1024x1024px",
    )
    image_medium = fields.Binary("Medium-sized image", attachment=True, track_visibility=True, help="Medium-sized image of this contact. It is automatically "\
        "resized as a 128x128px image, with aspect ratio preserved. "\
        "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True, track_visibility=True, help="Small-sized image of this contact. It is automatically "\
        "resized as a 64x64px image, with aspect ratio preserved. "\
        "Use this field anywhere a small image is required.")

    property_code_len = fields.Integer(
        "Property Code Length",
        track_visibility=True,
        default=lambda self: self.env.user.company_id.property_code_len)
    floor_code_len = fields.Integer(
        "Floor Code Length",
        track_visibility=True,
        default=lambda self: self.env.user.company_id.floor_code_len)
    unit_format = fields.Many2one("pms.format",
                                  "Unit Format",
                                  track_visibility=True,
                                  default=lambda self: self.env.user.company_id
                                  .space_unit_code_format.id)
    lease_format = fields.Many2one(
        "pms.format",
        "Lease Format",
        track_visibility=True,
        default=lambda self: self.env.user.company_id.lease_agre_format_id.id)
    pos_id_format = fields.Many2one(
        "pms.format",
        "POS ID  Format",
        track_visibility=True,
        default=lambda self: self.env.user.company_id.pos_id_format.id)
    prospect_format_id = fields.Many2one('pms.format',"Booking Format", track_visibility=True,
        default=lambda self: self.env.user.company_id.prospect_format_id.id)
    new_lease_term = fields.Many2one(
        "pms.leaseterms",
        "New Lease Term",
        track_visibility=True,
        default=lambda self: self.env.user.company_id.new_lease_term.id)
    extend_lease_term = fields.Many2one(
        "pms.leaseterms",
        "Extend Lease Term",
        track_visibility=True,
        default=lambda self: self.env.user.company_id.extend_lease_term.id)
    terminate_days = fields.Integer("Terminate Days",
                                    default=lambda self: self.env.user.
                                    company_id.pre_notice_terminate_term)
    extend_count = fields.Integer(
        "Extend Count",
        track_visibility=True,
        default=lambda self: self.env.user.company_id.extend_count)
    rentschedule_type = fields.Selection(
        [('prorated', "Prorated"), ('calendar', "Calendar")],
        track_visibility=True,
        default=lambda self: self.env.user.company_id.rentschedule_type,
        string="Rent Schedule Type",
    )
    api_integration = fields.Boolean(
        "API Integration",
        track_visibility=True,
    )
    count_unit = fields.Integer("Count Unit", compute="_get_count_unit")
    is_api_post = fields.Boolean("Posted")
    api_integration_id = fields.Many2one("pms.api.integration", "API Provider")
    meter_type = fields.Selection([('SHARED','Shared'),('NORMAL','Normal')], string="Meter Type", default="NORMAL")
    billing_circle_from = fields.Char("Billing Circle From")
    billing_circle_to = fields.Char("Billing Circle To")
    utilities_lines = fields.One2many("pms.utilities.lines",'property_id', string="Utilities")
    vacant_unit = fields.Integer("Vacant Unit", compute="_get_vacant_unit")
    occupy_unit = fields.Integer('Occupied Unit', compute="_get_occupied_unit")
    booking_lease = fields.Integer('Booking Lease', compute="_get_booking_lease")
    new_lease = fields.Integer('New Lease', compute="_get_new_lease")
    extend_lease =fields. Integer('Extend Lease', compute="_get_extend_lease")
    expire_lease = fields. Integer('Expire Soon', compute ="_get_expire_lease")

    _sql_constraints = [('code_unique', 'unique(code)',
                         'Your code is exiting in the database.')]


    # @api.model
    # @api.returns('self', lambda value: value.id)
    # def _property_default_get(self, object=False, field=False):
    #     """ Returns the default company (usually the user's company).
    #     The 'object' and 'field' arguments are ignored but left here for
    #     backward compatibility and potential override.
    #     """
    #     return self.env['res.users']._get_property()
    
    @api.multi
    @api.onchange('currency_id')
    def onchange_currency_id(self):
        country_id = None
        if self.currency_id:
            country_ids = self.env['res.country'].search([
                ('currency_id', '=', self.currency_id.id)
            ])
            if len(country_ids) > 1:
                country_id = country_ids[0]
            else:
                country_id = country_ids
        self.country_id = country_id

    @api.multi
    @api.onchange('code')
    def onchange_code(self):
        length = 0
        if self.code:
            length = len(self.code)
        if self.property_code_len:
            if length > self.property_code_len:
                raise UserError(
                    _("Property Code Length must not exceed %s characters." %
                      (self.property_code_len)))

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.code
            result.append((record.id, code))
        return result

    @api.multi
    def _get_count_unit(self):
        unit_ids = self.env['pms.space.unit'].search([('property_id', '=',
                                                       self.id),
                                                      ('active', '=', True)])
        for un in unit_ids:
            if un:
                self.count_unit += 1

    @api.multi
    def action_units(self):
        unit_ids = self.env['pms.space.unit'].search([('property_id', '=',
                                                       self.id),
                                                      ('active', '=', True)])

        action = self.env.ref(
            'property_management_system.action_space_all').read()[0]
        if len(unit_ids) > 1:
            action['domain'] = [('id', 'in', unit_ids.ids)]
        elif len(unit_ids) == 1:
            action['views'] = [(self.env.ref(
                'property_management_system.view_space_unit_form').id, 'form')]
            action['res_id'] = unit_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    # New Vacant Count Unit
    @api.multi
    def _get_vacant_unit(self):
        unit_ids = self.env['pms.space.unit'].search([('property_id', '=',
                                                       self.id),
                                                      ('active', '=', True)])
        today = date.today()
        for unit in unit_ids:
            lease_line_ids = self.env['pms.lease_agreement.line'].search([('property_id', '=', self.id),
                                                                        ('state','=','NEW'),
                                                                        ('unit_no','=',unit.id),
                                                                        ('start_date','<=',today),
                                                                        ('end_date','>=',today)
                                                                        ])
            if not lease_line_ids:    
                self.vacant_unit += 1

    @api.multi
    def vacant_action_units(self):
        unit_ids = self.env['pms.space.unit'].search([('property_id', '=',
                                                       self.id),
                                                      ('active', '=', True)])
        today = datetime.today()
        units= []
        for unit in unit_ids:
            lease_line_ids = self.env['pms.lease_agreement.line'].search([('property_id', '=', self.id),
                                                                        ('state','=','NEW'),
                                                                        ('unit_no','=',unit.name),
                                                                        ('start_date','<=',today),
                                                                        ('end_date','>=',today)
                                                                        ])
            if not lease_line_ids:
                units.append(unit.id) 

        action = self.env.ref(
            'property_management_system.action_space_all').read()[0]
        if len(units) > 1:
            action['domain'] = [('id', 'in', units)]
        elif len(unit_ids) == 1:
            action['views'] = [(self.env.ref(
                'property_management_system.view_space_unit_form').id, 'form')]
            action['res_id'] = unit_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    # New Occupied Count Unit
    @api.multi
    def _get_occupied_unit(self):
        unit_ids = self.env['pms.space.unit'].search([('property_id', '=',
                                                       self.id),
                                                      ('active', '=', True)])
        today = date.today()
        for unit in unit_ids:
            lease_line_ids = self.env['pms.lease_agreement.line'].search([('property_id', '=', self.id),
                                                                        ('state','=','NEW'),
                                                                        ('unit_no','=',unit.id),
                                                                        ('start_date','<=',today),
                                                                        ('end_date','>=',today)
                                                                        ])
            if lease_line_ids:    
                self.occupy_unit += 1

    @api.multi
    def occupied_action_units(self):
        unit_ids = self.env['pms.space.unit'].search([('property_id', '=',
                                                       self.id),
                                                      ('active', '=', True)])
        today = datetime.today()
        units= []
        for unit in unit_ids:
            lease_line_ids = self.env['pms.lease_agreement.line'].search([('property_id', '=', self.id),
                                                                        ('state','=','NEW'),
                                                                        ('unit_no','=',unit.name),
                                                                        ('start_date','<=',today),
                                                                        ('end_date','>=',today)
                                                                        ])
            if lease_line_ids:
                units.append(unit.id) 

        action = self.env.ref(
            'property_management_system.action_space_all').read()[0]
        if len(units) > 1:
            action['domain'] = [('id', 'in', units)]
        elif len(unit_ids) == 1:
            action['views'] = [(self.env.ref(
                'property_management_system.view_space_unit_form').id, 'form')]
            action['res_id'] = unit_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    # Booking Lease
    @api.multi
    def _get_booking_lease(self):
        unit_ids = self.env['pms.lease_agreement'].search([('property_id', '=',
                                                       self.id),('state','=','BOOKING')])
        for un in unit_ids:
            if un:
                self.booking_lease += 1

    @api.multi
    def booking_action_lease(self):
        unit_ids = self.env['pms.lease_agreement'].search([('property_id', '=',
                                                       self.id),('state','=','BOOKING')])

        action = self.env.ref(
            'property_management_system.action_lease_aggrement_all').read()[0]
        if len(unit_ids) > 1:
            action['domain'] = [('id', 'in', unit_ids.ids)]
        elif len(unit_ids) == 1:
            action['views'] = [(self.env.ref(
                'property_management_system.view_lease_aggrement_form').id, 'form')]
            action['res_id'] = unit_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    # New Lease
    @api.multi
    def _get_new_lease(self):
        unit_ids = self.env['pms.lease_agreement'].search(['&',('property_id', '=',
                                                       self.id),'|',('state','=','NEW'),('state','=','EXTENDED')])
        for un in unit_ids:
            if un:
                self.new_lease += 1
    
    @api.multi
    def new_action_lease(self):
        unit_ids = self.env['pms.lease_agreement'].search(['&',('property_id', '=',
                                                       self.id),'|',('state','=','NEW'),('state','=','EXTENDED')])

        action = self.env.ref(
            'property_management_system.action_lease_aggrement_all').read()[0]
        if len(unit_ids) > 1:
            action['domain'] = [('id', 'in', unit_ids.ids)]
        elif len(unit_ids) == 1:
            action['views'] = [(self.env.ref(
                'property_management_system.view_lease_aggrement_form').id, 'form')]
            action['res_id'] = unit_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def property_scheduler(self):
        values = None
        property_id = self.search([('api_integration', '=', True),
                                   ('is_api_post', '=', False)])
        if property_id:
            if property_id.api_integration_id:
                integ_obj = property_id.api_integration_id
                integ_line_obj = integ_obj.api_integration_line
                api_line_ids = integ_line_obj.search([('name', '=', "Property")
                                                      ])
                datas = api_rauth_config.APIData.get_data(
                    property_id, values, property_id, integ_obj, api_line_ids)
                if datas:
                    if datas.res:
                        response = json.loads(datas.res)
                        if 'responseStatus' in response:
                            if response['responseStatus'] == True:
                                if 'message' in response:
                                    if response['message'] == 'SUCCESS':
                                        for pl in property_id:
                                            pl.write({'is_api_post': True})

    @api.multi
    def _get_expire_lease(self):
        notify_month = self.new_lease_term.notify_period
        today = date.today()
        expire_date = today + relativedelta(months=notify_month)
        lease_ids = self.env['pms.lease_agreement'].search(['&',('property_id', '=', self.id),
                                                            '|',('state','=','NEW'),
                                                                ('state','=','EXTENDED'),
                                                            '|','&',('end_date','>=',today),
                                                                    ('end_date','<=',expire_date),
                                                                '&',('extend_to','>=',today),
                                                                    ('extend_to','<=',expire_date)])
        for lease in lease_ids:
            if lease:
                self.expire_lease += 1
    
    @api.multi
    def expire_action_lease(self):
        notify_month = self.new_lease_term.notify_period
        today = date.today()
        expire_date = today + relativedelta(months=notify_month)
        lease_ids = self.env['pms.lease_agreement'].search(['&',('property_id', '=', self.id),
                                                            '|',('state','=','NEW'),
                                                                ('state','=','EXTENDED'),
                                                            '|','&',('end_date','>=',today),
                                                                    ('end_date','<=',expire_date),
                                                                '&',('extend_to','>=',today),
                                                                    ('extend_to','<=',expire_date)])

        action = self.env.ref(
            'property_management_system.action_lease_aggrement_all').read()[0]
        if len(lease_ids) > 1:
            action['domain'] = [('id', 'in', lease_ids.ids)]
        elif len(lease_ids) == 1:
            action['views'] = [(self.env.ref(
                'property_management_system.view_lease_aggrement_form').id, 'form')]
            action['res_id'] = lease_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def _get_extend_lease(self):
        unit_ids = self.env['pms.lease_agreement'].search([('property_id', '=',
                                                       self.id),('state','=','EXTENDED')])
        for et in unit_ids:
            if et:
                self.extend_lease += 1
    
    @api.multi
    def extend_action_lease(self):
        unit_ids = self.env['pms.lease_agreement'].search([('property_id', '=',
                                                       self.id),('state','=','EXTENDED')])

        action = self.env.ref(
            'property_management_system.action_lease_aggrement_all').read()[0]
        if len(unit_ids) > 1:
            action['domain'] = [('id', 'in', unit_ids.ids)]
        elif len(unit_ids) == 1:
            action['views'] = [(self.env.ref(
                'property_management_system.view_lease_aggrement_form').id, 'form')]
            action['res_id'] = unit_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.model
    def create(self, values):
        # if 'property_management_id' in values:
        #     if values['property_management_id'][0][2] == []:
        #         raise UserError(
        #             _("Please set your management company for setting management rules."
        #             ))
        if 'image' in values:
            if values['image']:
                tools.image_resize_images(values, sizes={'image': (1024, None)})
        id = None
        id = super(PMSProperties, self).create(values)
        self.env.user.write({'property_id': [(4, id.id)]})
        self.env.user.write({'current_property_id': id.id})
        if id and 'is_api_post' not in values:
            property_id = None
            if 'api_integration' in values:
                    if 'api_integration_id' in values:
                        integ_obj = self.env['pms.api.integration'].browse(
                            values['api_integration_id'])
                        integ_line_obj = integ_obj.api_integration_line
                        api_line_ids = integ_line_obj.search([('name', '=',
                                                            "Property")])
                        datas = api_rauth_config.APIData.get_data(
                            id, values, property_id, integ_obj, api_line_ids)
                        if datas:
                            if datas.res:
                                response = json.loads(datas.res)
                                if 'responseStatus' in response:
                                    if response['responseStatus']:
                                        if 'message' in response:
                                            if response['message'] == 'SUCCESS':
                                                id.write({'is_api_post': True})
        return id

    @api.multi
    def write(self, vals):
        if 'property_management_id' in vals:
            if vals['property_management_id'][0][2] == []:
                raise UserError(
                    _("Please set your management company for setting management rules."
                      ))
        if 'image' in vals:
            if vals['image']:
                tools.image_resize_images(vals, sizes={'image': (1024, None)})
        id = None
        id = super(PMSProperties, self).write(vals)
        if 'api_integration' in vals and len(vals) == 1:
            return id
        if 'image' in vals and len(vals) == 3:
            return id
        if id and self.api_integration == True:
            property_id = self
            if self.api_integration_id:
                integ_obj = self.api_integration_id
                integ_line_obj = integ_obj.api_integration_line
                api_line_ids = integ_line_obj.search([('name', '=', "Property")
                                                      ])
                if 'is_api_post' in vals:
                    if vals['is_api_post']:
                        datas = api_rauth_config.APIData.get_data(
                            self, vals, property_id, integ_obj, api_line_ids)
                        if datas:
                            if datas.res:
                                response = json.loads(datas.res)
                                if 'responseStatus' in response:
                                    if response['responseStatus']:
                                        if 'message' in response:
                                            if response[
                                                    'message'] == 'SUCCESS':
                                                self.write(
                                                    {'is_api_post': True})
                else:
                    datas = api_rauth_config.APIData.get_data(
                        self, vals, property_id, integ_obj, api_line_ids)
                    if datas:
                        if datas.res:
                            response = json.loads(datas.res)
                            if 'responseStatus' in response:
                                if response['responseStatus']:
                                    if 'message' in response:
                                        if response['message'] == 'SUCCESS':
                                            self.write({'is_api_post': True})

        return id
    

class UtilitiesLines(models.Model):
    _name = "pms.utilities.lines"
    _description = "Utilities Lines"

    utilities_supply =fields.Many2one("pms.utilities.supply", string="Supply Type", store=True)
    utilities_type = fields.Many2one("pms.utilities.type", string="Utility Type", related="utilities_supply.utilities_type_id", store=True)
    digit = fields.Integer("Digit", default=8,store=True)
    property_id = fields.Many2one("pms.properties", "Property", store=True)

    


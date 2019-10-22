from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import pytz

_tzs = [
    (tz, tz)
    for tz in sorted(pytz.all_timezones,
                     key=lambda tz: tz if not tz.startswith('Etc/') else '_')
]


def _tz_get(self):
    return _tzs


class PMSProperties(models.Model):
    _name = 'pms.properties'
    _description = 'Property Management System'
    _order = "code"

    def get_uom_id(self):
        uom_id = uom_category_id = None
        uom_id = self.env['uom.uom'].search([('name', '=', "sqft")])
        if not uom_id:
            uom_category_id = self.env['uom.category'].search([('name', '=',
                                                                'Area')])
            if not uom_category_id:
                uom_category_id = self.env['uom.category'].create(
                    {'name': 'Area'})
            uom_id = self.env['uom.uom'].create({
                'name':
                'sqft',
                'cateogry_id':
                uom_category_id.id
            })
        return uom_id

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
        help="The properties's type is set the specific type.")
    uom_id = fields.Many2one("uom.uom",
                             "UOM",
                             required=True,
                             default=get_uom_id,
                             help="Unit Of Measure is need to set for Area.")
    bank_id = fields.Many2one('res.bank', "Bank Information")
    township = fields.Many2one("pms.township",
                               string='Township',
                               ondelete='restrict',
                               domain="[('city_id', '=?', city_id)]")
    city_id = fields.Many2one("pms.city",
                              string='City',
                              ondelete='restrict',
                              domain="[('state_id', '=?', state_id)]")
    state_id = fields.Many2one("res.country.state",
                               string='State',
                               ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    currency_id = fields.Many2one("res.currency",
                                  "Currency",
                                  default=default_get_curency,
                                  readonly=False,
                                  store=True)
    country_id = fields.Many2one('res.country',
                                 string='Country',
                                 default=default_get_country,
                                 readonly=False,
                                 requried=True,
                                 ondelete='restrict')
    name = fields.Char("Name", required=True, size=250)
    code = fields.Char("Code", size=250, required=True)
    gross_floor_area = fields.Float('GFA',
                                    digits=(16, 2),
                                    help="Gross Floor Area")
    net_lett_able_area = fields.Float('NLA',
                                      digits=(16, 2),
                                      help="Net Lett-able Area")
    web_site_url = fields.Char("Website", size=250, help="Website URL")
    is_autogenerate_posid = fields.Boolean("Auto Generate Pos ID",
                                           help="Auto Generating POS ID?")
    project_start_date = fields.Date("Project Start Date")
    target_open_date = fields.Date("Target Opening Date")
    actual_opening_date = fields.Date("Actual Openiing Date")
    timezone = fields.Selection(
        _tz_get,
        string='Timezone',
        default=lambda self: self._context.get('tz'),
        help=
        "The partner's timezone, used to output proper date and time values "
        "inside printed reports. It is important to set a value for this field. "
        "You should use the same timezone that is otherwise used to pick and "
        "render date and time values: your computer's timezone.")
    no = fields.Char()
    street = fields.Char()
    zip = fields.Char(change_default=True)
    property_contact_id = fields.Many2many(
        'res.partner',
        'pms_property_contact_rel',
        'property_id',
        'partner_id',
        string='Contacts',
        domain="[('is_company', '!=', True)]")
    property_management_id = fields.Many2many('res.company',
                                              'pms_property_managements_rel',
                                              'property_id',
                                              'partner_id',
                                              string='Managements')
    # leaseterms_line_id = fields.Many2many("pms.leaseterms",
    #                                       "pms_properties_leaseterms_rel",
    #                                       "properties_id",
    #                                       "leaseterm_id",
    #                                       string="LeaseTerms")
    image = fields.Binary(
        "Image",
        attachment=True,
        help=
        "This field holds the image used as avatar for this contact, limited to 1024x1024px",
    )
    image_medium = fields.Binary("Medium-sized image", attachment=True, help="Medium-sized image of this contact. It is automatically "\
        "resized as a 128x128px image, with aspect ratio preserved. "\
        "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True, help="Small-sized image of this contact. It is automatically "\
        "resized as a 64x64px image, with aspect ratio preserved. "\
        "Use this field anywhere a small image is required.")

    # company_id = fields.Many2many('res.partner')

    # next_pos_id = fields.Char("Next Pos ID")
    # pos_id_format = fields.Char("POS ID Format", size=250)
    _sql_constraints = [('code_unique', 'unique(code)',
                         'Your code is exiting in the database.')]

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
    def name_get(self):
        result = []
        for record in self:
            code = record.code
            result.append((record.id, code))
        return result

    @api.model
    def create(self, values):
        if values['property_management_id'][0][2] == []:
            raise UserError(
                _("Please set your management company for setting management rules."
                  ))
        if values['image']:
            tools.image_resize_images(values, sizes={'image': (1024, None)})
        return super(PMSProperties, self).create(values)

    @api.multi
    def write(self, vals):
        if 'property_management_id' in vals:
            if vals['property_management_id'][0][2] == []:
                raise UserError(
                    _("Please set your management company for setting management rules."
                      ))
        tools.image_resize_images(vals, sizes={'image': (1024, None)})
        return super(PMSProperties, self).write(vals)

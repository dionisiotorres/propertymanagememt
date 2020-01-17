from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from odoo.addons.property_management_system.models import api_rauth_config


class PMSSpaceUnit(models.Model):
    _name = 'pms.space.unit'
    _inherit = ['mail.thread']
    _description = "Space Units"
    _order = "parent_id"

    def get_property_id(self):
        if not self.property_id:
            property_id = None
            if not self.env.user.property_id:
                raise UserError(_("Please set property in user setting."))
            property_id = self.env.user.property_id[0]
            return property_id

    def get_floor(self):
        if not self.floor_id:
            floor_ids = self.env['pms.floor'].search([], order='id asc')
            property_id = self.property_id or self.env.user.property_id[0]
            if floor_ids:
                floor_id = floor_ids[0]
                return floor_id
            else:
                val = {
                    'name': 'Floor 1',
                    'code': 'F1',
                    'property_id': property_id.id,
                    'floor_code_ref': '01',
                    'active': True
                }
                floor = self.env['pms.floor'].create(val)
                return floor

    name = fields.Char("Unit No",
                       compute='get_unit_no',
                       store=True,
                       track_visibility=True,
                       readonly=True)
    unit_code = fields.Char("Unit",
                            compute='get_unit_no',
                            store=True,
                            track_visibility=True,
                            readonly=True)
    property_id = fields.Many2one("pms.properties",
                                  string="Property",
                                  default=get_property_id,
                                  track_visibility=True,
                                  required=True)
    floor_id = fields.Many2one("pms.floor",
                               string="Floor",
                               default=get_floor,
                               track_visibility=True,
                               required=True)
    floor_code = fields.Char(string="Floor Code",
                             related="floor_id.code",
                             track_visibility=True,
                             store=False)
    unit_no = fields.Char("Space Unit No",
                          store=True,
                          required=True,
                          track_visibility=True)
    parent_id = fields.Many2one("pms.space.unit",
                                "Parent",
                                store=True,
                                track_visibility=True)
    # unittype_id = fields.Many2one("pms.applicable.space.type",
    #                               "Type",
    #                               track_visibility=True)
    spaceunittype_id = fields.Many2one("pms.applicable.space.type",
                                       "Type",
                                       track_visibility=True)
    uom = fields.Many2one("uom.uom",
                          "UOM",
                          related="property_id.uom_id",
                          store=True,
                          track_visibility=True)
    area = fields.Integer("Area", track_visibility=True)
    start_date = fields.Date("Start Date", track_visibility=True)
    end_date = fields.Date("End Date", track_visibility=True)
    status = fields.Selection([('vacant', 'Vacant'), ('occupied', 'Occupied')],
                              string="Status",
                              default="vacant",
                              track_visibility=True)
    rate = fields.Float("Rate", track_visibility=True)
    min_rate = fields.Float("Min Rate",
                            digits=dp.get_precision('Min Rate'),
                            track_visibility=True)
    max_rate = fields.Float("Max Rate",
                            digits=dp.get_precision('Max Rate'),
                            track_visibility=True)
    remark = fields.Text("Remark", track_visibility=True)

    facility_line = fields.Many2many("pms.facilities",
                                     "pms_unit_facility_rel",
                                     "unit_id",
                                     "facilities_id",
                                     "Facilities",
                                     track_visibility=True)
    rent_record = fields.Many2many("pms.rent_record",
                                   "pms_unit_record_rel",
                                   "unit_id",
                                   "record_id",
                                   "Add Records",
                                   track_visibility=True)
    active = fields.Boolean("Active", default=True)
    booking_date = fields.Date("Booking Date")
    booking_expired_date = fields.Date("Booking Expired Date")

    @api.multi
    @api.onchange('end_date')
    def onchange_active(self):
        if self.end_date:
            self.active = False
        else:
            self.active = True

    @api.one
    @api.depends('unit_no', 'floor_id', 'property_id')
    def get_unit_no(self):
        if self.floor_id:
            self.unit_code = self.floor_id.floor_code_ref + '-'
        if self.property_id:
            if self.property_id.unit_format:
                format_ids = self.env['pms.format.detail'].search(
                    [('format_id', '=', self.property_id.unit_format.id)],
                    order='position_order asc')
                val = []
                for fid in format_ids:
                    if fid.value_type == 'dynamic':
                        if self.floor_id.code and fid.dynamic_value == 'floor code':
                            val.append(self.floor_id.code)
                        if self.floor_id.floor_code_ref and fid.dynamic_value == 'floor ref code':
                            val.append(self.floor_id.floor_code_ref)
                        if self.property_id.code and fid.dynamic_value == 'property code':
                            val.append(self.property_id.code)
                    if fid.value_type == 'fix':
                        if self.unit_no or self.floor_id:
                            val.append(fid.fix_value)
                    if fid.value_type == 'digit':
                        if self.unit_no and len(
                                self.unit_no) > fid.digit_value:
                            raise UserError(
                                _("Please Unit Length less than your format digit."
                                  ))
                    if fid.value_type == 'datetime':
                        val.append(fid.datetime_value)
                space = []
                self.name = ''
                self.unit_code = ''
                if len(val) > 0:
                    for l in range(len(val)):
                        self.name += str(val[l])
                        self.unit_code += str(val[l])
                    if self.unit_no:
                        self.name += str(self.unit_no)

            else:
                raise UserError(_("Please setup your unit format in Property"))
        length = 0
        if self.name:
            length = len(self.name)
        if self.property_id.unit_code_len:
            if length > self.property_id.unit_code_len:
                raise UserError(
                    _("Please set your code length less than %s." %
                      (self.property_id.unit_code_len)))

    # @api.multi
    # @api.onchange('name')
    # def onchange_name(self):
    #     length = 0
    #     if self.name:
    #         length = len(self.name)
    #     if self.env.user.company_id.space_unit_code_len:
    #         if length > self.env.user.company_id.space_unit_code_len:
    #             raise UserError(
    #                 _("Please set your code length less than %s." %
    #                   (self.env.user.company_id.space_unit_code_len)))

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.name
            result.append((record.id, code))
        return result

    @api.model
    def create(self, values):
        floor_id = self.env['pms.floor'].search([('id', '=',
                                                  values['floor_id'])])
        property_id = floor_id.property_id
        if values['property_id'] != property_id.id:
            raise UserError(
                _('Please set floor in  %s property.') % values['property_id'])
        unit = ''
        if property_id.unit_format:
            for line in property_id.unit_format.format_line_id:
                if line.value_type == 'dynamic':
                    if line.dynamic_value == 'floor ref code':
                        unit += str(floor_id.floor_code_ref)
                    if line.dynamic_value == 'floor code':
                        unit += str(floor_id.floor_code)
                if line.value_type == 'fix':
                    unit += str(line.fix_value)
                if line.value_type == 'digit':
                    unit += str(values['unit_no'])
                unit_ids = self.search([('name', '=', unit),
                                        ('property_id', '=',
                                         values['property_id']),
                                        ('active', '=', True)])
                if unit_ids:
                    raise UserError(
                        _("%s Units is exiting in the database." % (unit)))
                # else:
                #     unit_id = self.search([('name', '=', unit),
                #                            ('property_id', '=',
                #                             values['property_id']),
                #                            ('active', '=', True)])
                #     unit_id1 = self.search([
                #         ('name', '=', unit),
                #         ('property_id', '=', values['property_id']),
                #         ('start_date', '>=', values['start_date']),
                #         ('end_date', '=', False)
                #     ])
                #     if unit_id and not unit_id.end_date:
                #         raise UserError(
                #             _("%s Units is exiting in the database and please set end date and retry."
                #               % (unit)))

        id = None
        id = super(PMSSpaceUnit, self).create(values)
        # if id:
        #     property_obj = self.env['pms.properties'].browse(
        #         values['property_id'])
        #     integ_obj = self.env['pms.api.integration']
        #     api_type_obj = self.env['pms.api.type'].search([('name', '=',
        #                                                      "SpaceUnit")])
        #     datas = api_rauth_config.APIData(id, values, property_obj,
        #                                      integ_obj, api_type_obj)
        #     if values['facility_line']:
        #         for fl in values['facility_line'][0][2]:
        #             facility_id = self.env['pms.facilities'].browse(fl)
        #             property_objs = self.env['pms.properties'].browse(
        #                 facility_id.property_id.id)
        #             integ_objs = self.env['pms.api.integration']
        #             api_type_objs = self.env['pms.api.type'].search([
        #                 ('name', '=', "Facilities")
        #             ])
        #  datas = api_rauth_config.APIData(id, values, property_obj,
        #                                      integ_obj, api_type_obj)
        return id

    @api.multi
    def write(self, val):
        property_id = None
        if 'floor_id' in val or 'property_id' in val:
            if 'floor_id' in val:
                property_id = self.env['pms.floor'].search([
                    ('id', '=', val['floor_id'])
                ]).property_id
            if 'property_id' in val:
                if property_id:
                    if val['property_id'] != property_id.id:
                        raise UserError(
                            _('Please set floor in  %s property.') %
                            self.env['pms.properties'].search(
                                [('id', '=', val['property_id'])]).name)
                else:
                    if val['property_id'] != self.floor_id.property_id.id:
                        raise UserError(
                            _('Please set floor in  %s property.') %
                            self.env['pms.properties'].search(
                                [('id', '=', val['property_id'])]).name)
            else:
                if self.property_id != property_id.id:
                    raise UserError(
                        _('Please set floor in  %s property.') %
                        self.property_id.name)
        return super(PMSSpaceUnit, self).write(val)


class PMSRentRecord(models.Model):
    _name = "pms.rent_record"
    _description = "Rent Records"

    def get_property_id(self):
        property_id = space_unit_id = active_id = None
        active_id = self._context.get('active_id')
        space_unit_id = self.env['pms.space.unit'].browse(int(active_id))
        property_id = space_unit_id.property_id
        return property_id

    sequence_no = fields.Integer("No", track_visibility=True)
    name = fields.Text("Remark", track_visibility=True)
    property_id = fields.Many2one("pms.properties",
                                  "Property",
                                  default=get_property_id)

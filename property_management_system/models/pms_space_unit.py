import json
import datetime
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.addons import decimal_precision as dp
from odoo.addons.property_management_system.models import api_rauth_config


class PMSSpaceUnit(models.Model):
    _name = 'pms.space.unit'
    _inherit = ['mail.thread']
    _description = "Space Units"
    _order = "parent_id"

    def _get_property(self):
        return self.env.user.current_property_id
        

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

    name = fields.Char("Unit No", store=True, compute="get_unit_code", track_visibility=True)
    unit_code = fields.Char("Unit", compute="get_unit_code", readonly=True)
    property_id = fields.Many2one("pms.properties",
                                  string="Property",
                                  default=_get_property,
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
                          required=True,
                          readonly=False,
                          store=True)
    parent_id = fields.Many2one("pms.space.unit",
                                "Parent",
                                store=True,
                                track_visibility=True)
    spaceunittype_id = fields.Many2one("pms.applicable.space.type",
                                       "Unit Type",
                                       required=True,
                                       track_visibility=True)
    uom = fields.Many2one("uom.uom",
                          "UOM",
                          related="property_id.uom_id",
                          store=True,
                          track_visibility=True)
    area = fields.Float("Area", track_visibility=True)
    start_date = fields.Date("Start Date",
                             track_visibility=True,
                             required=True,
                             help='When the unit is able to use.')
    end_date = fields.Date("End Date",
                           track_visibility=True,
                           help='When the unit is unactive.')
    status = fields.Selection([('vacant', 'Vacant'), ('occupied', 'Occupied')],
                              string="Status",
                              default="vacant",
                              track_visibility=True,
                              help='Current status of the unit.')
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
    active = fields.Boolean("Active", default=True)
    is_api_post = fields.Boolean("Posted")
    meter_no = fields.Char("Meters", compute="get_meter_no", readonly=True)
    config_flag = fields.Selection([('new', 'N'), ('config', 'C'),
                                    ('survey', 'S')], "Config Flag")
    resurvey_date = fields.Date("Resurvey Date")
    space_facility_line = fields.One2many("pms.space.unit.facility.lines","unit_id","Space Facility lines",track_visibility=True)
    job_ids = fields.One2many("pms.space.unit.job.line","unit_id","Job Line")
    active_lease = fields.Integer('Active Lease', compute="_get_active_lease")
    history_lease = fields.Integer('History Lease', compute="_get_history_lease")
    color = fields.Integer(string='Color Index', compute="set_kanban_color")

    def set_kanban_color(self):
        for record in self:
            color = 0
            if record.status == 'vacant':
                color = 3
            elif record.status == 'occupied':
                color = 4
            record.color = color

    @api.multi
    @api.onchange('end_date')
    def onchange_end_date(self):
        today = datetime.now()
        if self.end_date:
            if self.end_date >= today.date():
                self.active = True
            else:
                self.active = False
            for line in self.space_facility_line:
                line.end_date = self.end_date
                line.write({'inuse':False})


    def spaceunit_unactive_schedular(self):
        today = datetime.now()
        spaceunit_ids = self.search([('end_date', '!=', None),
                                     ('active', '=', True)])
        if spaceunit_ids:
            for sp in spaceunit_ids:
                if sp.end_date:
                    if sp.end_date <= today.date():
                        sp.active = False

    @api.one
    @api.depends('unit_no', 'floor_id', 'property_id')
    def get_unit_code(self):
        if self.floor_id:
            self.unit_code = self.floor_id.floor_code_ref + '-'
        if self.property_id:
            if self.property_id.unit_format:
                format_ids = self.env['pms.format.detail'].search(
                    [('format_id', '=', self.property_id.unit_format.id)],
                    order='sequence asc')
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
                    if fid.value_type == 'datetime':
                        val.append(fid.datetime_value)
                space = []
                self.unit_code = ''
                if len(val) > 0:
                    for l in range(len(val)):
                        self.unit_code += str(val[l])
                if self.unit_no:
                    self.name = self.unit_code + self.unit_no
            else:
                raise UserError(_("Please define unit format at first."))

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.name
            result.append((record.id, code))
        return result

    @api.one
    @api.depends('facility_line')
    def get_meter_no(self):
        meters = ''
        if self.facility_line:
            for fl in self.facility_line:
                meter = ''
                meter += fl.name
                if fl.facilities_line:
                    meter += "("
                    f_meter = ''
                    for fsl in fl.facilities_line:
                        if len(fl.facilities_line) > 1:
                            if f_meter == '':
                                f_meter += fsl.source_type_id.code
                            else:
                                f_meter += "|" + fsl.source_type_id.code
                        else:
                            f_meter += fsl.source_type_id.code
                    meter += f_meter
                    meter += ")"
                    if meters != '':
                        meters += ',' + meter
                    else:
                        meters += meter
            self.meter_no = meters

    
    @api.multi
    def _get_active_lease(self):
        lease_line_id = self.env['pms.lease_agreement.line'].search(['&',('property_id', '=',self.property_id.id),
                                                                '|',('state','=','NEW'),
                                                                    ('state','=','EXTENDED'),
                                                                    ('unit_no','=',self.id)])

        if lease_line_id:
            self.active_lease += 1
    
    @api.multi
    def active_action_lease(self):
        lease_line_id = self.env['pms.lease_agreement.line'].search(['&',('property_id', '=',self.property_id.id),
                                                                '|',('state','=','NEW'),
                                                                    ('state','=','EXTENDED'),
                                                                    ('unit_no','=',self.id)])
        lease = self.env['pms.lease_agreement']                                                            
        if lease_line_id:
            lease = self.env['pms.lease_agreement'].search([('property_id', '=',self.property_id.id),
                                                            ('lease_agreement_line','=',lease_line_id.id),
                                                            ])
        action = self.env.ref(
            'property_management_system.action_lease_aggrement_all').read()[0]
        if len(lease) > 1:
            action['domain'] = [('id', 'in', lease.ids)]
        elif len(lease) == 1:
            action['views'] = [(self.env.ref(
                'property_management_system.view_lease_aggrement_form').id, 'form')]
            action['res_id'] = lease.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    # History Lease
    @api.multi
    def _get_history_lease(self):
        lease_line_ids = self.env['pms.lease_agreement.line'].search(['&',('property_id', '=',self.property_id.id),
                                                                '|',('state','=','RENEWED'),
                                                                '|',('state','=','CANCELLED'),
                                                                    ('state','=','PRE-TERMINATED'),
                                                                    ('unit_no','=',self.id)])

        if lease_line_ids:
            for lease_line_id in lease_line_ids:
                self.history_lease += 1
    
    @api.multi
    def history_action_lease(self):
        lease_line_ids = self.env['pms.lease_agreement.line'].search(['&',('property_id', '=',self.property_id.id),
                                                                '|',('state','=','RENEWED'),
                                                                '|',('state','=','CANCELLED'),
                                                                    ('state','=','PRE-TERMINATED'),
                                                                    ('unit_no','=',self.id)])
        action = self.env.ref('property_management_system.action_lease_aggrement_all').read()[0]
        if len(lease_line_ids) > 1:
            action['domain'] = [('lease_agreement_line', 'in', lease_line_ids.ids)]
        elif len(lease_line_ids) == 1:
            form_view = [(self.env.ref('property_management_system.view_lease_aggrement_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [
                    (state, view)
                    for state, view in action['views'] if view != 'form'
                ]
            else:
                action['views'] = form_view
            action['res_id'] = lease_line_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_type': 'out_building',
        }
        return action

    def space_unit_scheduler(self):
        values = None
        property_ids = []
        property_id = self.env['pms.properties'].search([('api_integration',
                                                          '=', True)])
        for pro in property_id:
            property_ids = pro
            spacetype = spappid = []
            space_type_ids = self.env['pms.space.type'].search([('is_export','=',True)])
            for sp in space_type_ids:
                spacetype.append(sp.id)
            applicable_space_ids = self.env['pms.applicable.space.type'].search([('space_type_id','in',spacetype)])
            for sapt in applicable_space_ids:
                spappid.append(sapt.id)
            spaceunit_ids = self.search([('is_api_post', '=', False),
                                         ('property_id', '=', property_ids.id),
                                         ('spaceunittype_id','in',spappid)
                                         ])
            if spaceunit_ids:
                integ_obj = property_ids.api_integration_id
                integ_line_obj = integ_obj.api_integration_line
                api_line_ids = integ_line_obj.search([('name', '=',
                                                       "SpaceUnit")])
                datas = api_rauth_config.APIData.get_data(
                    spaceunit_ids, values, property_id, integ_obj,
                    api_line_ids)
                if datas:
                    if datas.res:
                        response = json.loads(datas.res)
                        if 'responseStatus' in response:
                            if response['responseStatus']:
                                if 'message' in response:
                                    if response['message'] == 'SUCCESS':
                                        for fc in spaceunit_ids:
                                            fc.write({'is_api_post': True})

    @api.model
    def create(self, values):
        unit = ''
        floor_id = self.env['pms.floor'].search([('id', '=',
                                                  values['floor_id'])])
        property_id = floor_id.property_id
        if values['property_id'] != property_id.id:
            property_code = self.env['pms.properties'].browse(
                values['property_id'])
            raise UserError(
                _('Floor %s is not exit in the %s Property.') %
                (floor_id.code, property_code.code))
        if property_id.unit_format:
            for line in property_id.unit_format.format_line_id:
                if line.value_type == 'dynamic':
                    if line.dynamic_value == 'floor ref code':
                        unit += str(floor_id.floor_code_ref)
                    if line.dynamic_value == 'floor code':
                        unit += str(floor_id.code)
                if line.value_type == 'fix':
                    unit += str(line.fix_value)
                if line.value_type == 'digit':
                    unit += str(values['unit_no'])
                    if len(values['unit_no']) > line.digit_value:
                        raise UserError(
                            _("Total Unit length must not exceed %s characters."
                              % (line.digit_value)))
                unit_ids = self.search([
                    ('name', '=', unit),
                    ('property_id', '=', values['property_id']),
                    ('end_date', '>', values['start_date']),
                ])
                unit_ids1 = self.search([('name', '=', unit),
                                         ('property_id', '=',
                                          values['property_id']),
                                         ('start_date', '!=', False),
                                         ('end_date', '=', False),
                                         ('active', '=', True)])
                if unit_ids or unit_ids1:
                    raise UserError(_("%s is already existed." % (unit)))
            values['name'] = unit
        if 'facility_line' in values:
            for fl in values['facility_line']:
                print(fl[2])
                if fl[2]:
                    fac_id = self.env['pms.facilities'].browse(fl[2])
                    fac_id.write({'status': True})
        id = None
        id = super(PMSSpaceUnit, self).create(values)
        exported = id.spaceunittype_id.space_type_id.is_export
        if id and exported:
            if 'is_api_post' not in values:
                property_obj = self.env['pms.properties']
                property_id = property_obj.browse(values['property_id'])
                if property_id.api_integration:
                    if property_id.api_integration_id:
                        integ_obj = property_id.api_integration_id
                        integ_line_obj = integ_obj.api_integration_line
                        api_line_ids = integ_line_obj.search([('name', '=',
                                                            "SpaceUnit")])
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

    
    def generate_facilities(self):
        tree_view_id = self.env.ref('property_management_system.view_facilities_tree').ids
        form_view_id = self.env.ref('property_management_system.view_facilities_form').ids
        inuse = False
        domain = [('inuse','=',inuse)]
        return {
            'name': 'ZPMS',
            'view_mode': 'tree',
            'views': [[tree_view_id, 'tree'], [form_view_id, 'form']],
            'res_model': 'pms.facilities',
            'domain': domain,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

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
        if 'facility_line' in val:
            for fl in val['facility_line']:
                if fl[2]:
                    fac_id = self.env['pms.facilities'].browse(fl[2])
                    fac_id.write({'status': True})
        id = None
        id = super(PMSSpaceUnit, self).write(val)
        exported = self.spaceunittype_id.space_type_id.is_export
        if id and exported:
            property_id = None
            if 'property_id' in val:
                property_id = val['property_id']
            else:
                property_id = self.property_id.id
            property_obj = self.env['pms.properties']
            property_ids = property_obj.browse(property_id)
            if property_ids.api_integration:
                if property_ids.api_integration_id:
                    integ_obj = property_ids.api_integration_id
                    integ_line_obj = integ_obj.api_integration_line
                    api_line_ids = integ_line_obj.search([('name', '=',
                                                           "SpaceUnit")])
                    datas = None
                    if 'is_api_post' in val:
                        if not val['is_api_post']:
                            datas = api_rauth_config.APIData.get_data(self, val, property_ids, integ_obj, api_line_ids)
                        else:
                            datas = None
                    else:
                        if self.is_api_post:
                            datas = api_rauth_config.APIData.get_data(self, val, property_ids, integ_obj, api_line_ids)
                    if datas:
                        if datas.res:
                            response = json.loads(datas.res)
                            if response['responseStatus'] and response[
                                    'message'] == 'SUCCESS':
                                self.write({'is_api_post': True})
        return id

    @api.one
    def do_action(self):
        return True

class PMSSpaceUnitJobLine(models.Model):
    _name ="pms.space.unit.job.line"
    _description = "Unit Jobs"
    _order = "sequence,name"

    engineer_id = fields.Many2one("res.partner","Engineer", domain=[('is_company','=',False)], required=True)
    recommend_by = fields.Many2one("res.partner", domain=[('is_company','=',False)], string="Recommend By")
    name = fields.Char("Job Title", required=True)
    description = fields.Text("Description", required=True)
    remark = fields.Text("Remark")
    unit_id = fields.Many2one("pms.space.unit", "Space Unit")
    sequence = fields.Integer(track_visibility=True)
    index = fields.Integer(compute='_compute_index')
    status = fields.Selection([('draft','Draft'),('done',"Done")],default="draft", string="Status")

    @api.one
    def _compute_index(self):
        cr, uid, ctx = self.env.args
        self.index = self._model.search_count(cr,uid,[('sequence','<',self.sequence)],context=ctx) + 1

    def action_done(self):
        if self.state =="draft":
            self.write({'state':"done"})

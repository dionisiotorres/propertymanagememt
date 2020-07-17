# -*- coding: utf-8 -*-
import json
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from odoo.addons.property_management_system.models import api_rauth_config

class PMSSpaceUnitFacilityLines(models.Model):
    _name = 'pms.space.unit.facility.lines'
    _description = "PMS Space Facility Lines"

    @api.one
    def _get_property(self):
        return self.env.user.current_property_id

    facility_id = fields.Many2one("pms.facilities","Utilities")
    facility_line_id = fields.Many2one("pms.facility.lines",
                                  "Facility Lines",
                                  track_visibility=True)
    source_type_id = fields.Many2one('pms.utilities.supply',
                                     "Utilities Supply",
                                     required=True,
                                     track_visibility=True)
    start_reading_date = fields.Date("Start Date", track_visibility=True)
    start_reading_value = fields.Float("Start Reading Value", track_visibility=True)
    end_date = fields.Date("End Date", track_visibility=True)
    status = fields.Boolean("Status", default=True, track_visibility=True)
    property_id = fields.Many2one("pms.properties",
                                  "Property",
                                  default=_get_property,
                                  required=True,
                                  store=True,
                                  track_visibility=True)
    unit_id = fields.Many2one("pms.space.unit","Space Unit")
    inuse = fields.Boolean("In Use", default=False)
    is_api_post = fields.Boolean("Posted")
    digit = fields.Integer("Digit",track_visibility=True,help='The maximun capicity to display on equipment screen(esp. meter)')
    interface_type = fields.Selection([('auto', 'Auto'), ('manual', 'Manual'),
                                       ('mobile', 'Mobile')],
                                      "Data Interface Type",
                                      track_visibility=True)
    meter_type = fields.Char("Meter Type",
                               track_visibility=True,
                               help='Type of Electric Meters')    

    def suf_scheduler(self):
        values = None
        property_id = None
        property_ids = self.env['pms.properties'].search([
            ('api_integration', '=', True), ('api_integration_id', '!=', False)
        ])
        for pro in property_ids:
            property_id = pro
            facility_ids = self.search([('is_api_post', '=', False),
                                        ('property_id', '=', property_id.id),
                                        ('inuse','=',True)])
            if facility_ids:
                integ_obj = property_id.api_integration_id
                integ_line_obj = integ_obj.api_integration_line
                api_line_ids = integ_line_obj.search([('name', '=',
                                                    "SpaceUnitFacilities")])
                datas = api_rauth_config.APIData.get_data(
                    facility_ids, values, property_id, integ_obj, api_line_ids)
                if datas:
                    if datas.res:
                        response = json.loads(datas.res)
                        if 'responseStatus' in response:
                            if response['responseStatus']:
                                if 'message' in response:
                                    if response['message'] == 'SUCCESS':
                                        for fc in facility_ids:
                                            fc.write({'is_api_post': True})
    
    @api.model
    def create(self,values):
        res = super(PMSSpaceUnitFacilityLines,self).create(values)
        if 'unit_id' in values:
            unit_id = self.env['pms.space.unit'].browse(values['unit_id'])
            if unit_id.spaceunittype_id.space_type_id.is_export:    
                if 'facility_id' in values:
                    facility_id = self.env['pms.facilities'].browse(values['facility_id'])
                    values['utilities_type_id'] = facility_id.utilities_type_id.export_utilities_type
                    values['start_reading_date'] = facility_id.install_date
                    values['remark'] = facility_id.remark
                if 'facility_line_id' in values:
                    facility_line_id = self.env['pms.facility.lines'].browse(values['facility_line_id'])
                    values['utilities_type_id'] = facility_line_id.source_type_id.export_supply_type
                values['id']= res.id
                property_id = self.env['pms.properties'].browse(values['property_id'])
                integ_objs = property_id.api_integration_id
                integ_line_obj = integ_objs.api_integration_line
                api_line_ids = integ_line_obj.search([('name', '=', "SpaceUnitFacilities")])
                datas = api_rauth_config.APIData.get_data(self, values, property_id, integ_objs,api_line_ids)
                if datas:
                    if datas.res:
                        response = json.loads(datas.res)
                        if 'responseStatus' in response:
                            if response['responseStatus']:
                                if 'message' in response:
                                    if response['message'] == 'SUCCESS':
                                        self.write({'is_api_post':True})

    @api.multi
    def write(self, values):
        result = super(PMSSpaceUnitFacilityLines, self).write(values)
        if len(values) > 0 and self.inuse:
            property_id = self.property_id
            integ_objs = property_id.api_integration_id
            integ_line_obj = integ_objs.api_integration_line
            api_line_ids = integ_line_obj.search([('name', '=', "SpaceUnitFacilities")])
            datas = api_rauth_config.APIData.get_data(self, values, property_id, integ_objs, api_line_ids)
            if datas:
                if datas.res:
                    response = json.loads(datas.res)
                    if 'responseStatus' in response:
                        if response['responseStatus']:
                            if 'message' in response:
                                if response['message'] == 'SUCCESS':
                                    self.write({'is_api_post': True})
        return result

    @api.multi
    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date:
            self.write({'inuse': False})
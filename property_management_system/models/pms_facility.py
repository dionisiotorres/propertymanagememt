# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from odoo.addons.property_management_system.models import api_rauth_config


class PMSFacilities(models.Model):
    _name = 'pms.facilities'
    _description = "Facilities"

    name = fields.Char(default="Utilities No",
                       related='utilities_no.name',
                       readonly=True,
                       store=True,
                       required=True,
                       track_visibility=True)
    utilities_type_id = fields.Many2one('pms.utilities.supply.type',
                                        "Utilities Supply Type",
                                        required=True,
                                        track_visibility=True)
    utilities_no = fields.Many2one("pms.equipment",
                                   "Utilities No",
                                   required=True,
                                   track_visibility=True)
    interface_type = fields.Selection([('auto', 'Auto'), ('manual', 'Manual'),
                                       ('mobile', 'Mobile')],
                                      "Data Interface Type",
                                      track_visibility=True)
    remark = fields.Text("Remark", track_visibility=True)
    status = fields.Boolean("Status",
                            default=True,
                            track_visibility=True,
                            help='Current Status of utilities.')
    facilities_line = fields.One2many("pms.facility.lines",
                                      "facility_id",
                                      "Facility Lines",
                                      track_visibility=True)
    property_id = fields.Many2one("pms.properties",
                                  "Property",
                                  required=True,
                                  track_visibility=True)
    count_unit = fields.Integer("Count Unit", compute="_get_count_unit")
    install_date = fields.Date("Installation Date",
                               track_visibility=True,
                               help='The date of Facility installation date.')
    e_meter_type = fields.Char("E Meter Type",
                               track_visibility=True,
                               help='Type of Electric Meters')
    last_rdate = fields.Date("LMR Date", help='Last Month Reading Date.')
    lmr_rvalue = fields.Char("LMR Date", help='Last Month Reading Value.')

    # _sql_constraints = [('name_unique', 'unique(name)',
    #                      'Your name is exiting in the database.')]

    # @api.onchange('utilities_type_id')
    # def onchange_utilities_type_id(self):
    #     parent_id = []
    #     domain = {}
    #     utilities_id = None
    #     if self.utilities_type_id != None:
    #         utilities_ids = self.env['pms.utilities.source.type'].search([
    #             ('utilities_type_id', '=', self.utilities_type_id.id)
    #         ])
    #         for loop in utilities_ids:
    #             parent_id.append(loop.id)
    #         domain = {'source_type_id': [('id', 'in', parent_id)]}
    #     return {'domain': domain}

    @api.multi
    def _get_count_unit(self):
        count = 0
        unit_ids = self.env['pms.space.unit'].search([('facility_line', '=',
                                                       self.id),
                                                      ('active', '=', True)])
        for unit in unit_ids:
            self.count_unit += 1

    @api.multi
    def action_units(self):
        unit_ids = self.env['pms.space.unit'].search([('facility_line', '=',
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

    @api.model
    def create(self, values):
        id = None
        ldata = []
        emetertype = lmrvalue = None
        if 'facilities_line' in values:
            if len(values['facilities_line']) > 0:
                for line in values['facilities_line']:
                    ldata.append(line[2]['source_type_id'])
                    utiliy_id = self.env['pms.utilities.source.type'].browse(
                        line[2]['source_type_id'])
                    if emetertype:
                        emetertype += " | " + str(utiliy_id.code)
                        lmrvalue += " | " + str(line[2]['lmr_value'])
                    if not emetertype:
                        emetertype = str(utiliy_id.code)
                        lmrvalue = str(line[2]['lmr_value'])
                        lmrdate = line[2]['lmr_date']

                dupes = [x for n, x in enumerate(ldata) if x in ldata[:n]]
                if dupes:
                    raise UserError(_("Supply Source Type is same."))
                else:

                    fac_ids = self.search([('utilities_no', '=',
                                            values['utilities_no'])])
                    if fac_ids:
                        for fid in fac_ids:
                            if fid.facilities_line:
                                for fl in fid.facilities_line:
                                    if fl.source_type_id.id in ldata:
                                        raise UserError(
                                            _("Plese can not set duplicate supply sourec type."
                                              ))
        if emetertype:
            values['e_meter_type'] = emetertype
        if lmrvalue:
            values['lmr_value'] = lmrvalue
        if lmrdate:
            values['lmr_date'] = lmrdate
        id = super(PMSFacilities, self).create(values)
        # if id:
        # property_obj = self.env['pms.properties'].browse(
        #     values['property_id'])
        # integ_obj = self.env['pms.api.integration']
        # api_type_obj = self.env['pms.api.type'].search([
        #     ('name', '=', "SpaceUnitFacility")
        # ])
        # datas = api_rauth_config.APIData(id, values, property_obj,
        #                                  integ_obj, api_type_obj)
        return id

    @api.multi
    def write(self, values):
        ldata = []
        emetertype = lmrvalue = utiliy_id = lmrdate = None
        if 'facilities_line' in values:
            if len(values['facilities_line']) > 0:
                for line in values['facilities_line']:
                    if line[2] == False:
                        fids = self.env['pms.facility.lines'].browse(line[1])
                        if lmrvalue:
                            lmrvalue += " | " + str(fids.start_reading_value)
                        if not lmrvalue:
                            lmrvalue = str(fids.start_reading_value)
                    if line[2] != False:
                        if 'source_type_id' in line[2]:
                            ldata.append(line[2]['source_type_id'])
                            utiliy_id = self.env[
                                'pms.utilities.source.type'].browse(
                                    line[2]['source_type_id'])
                        if emetertype:
                            emetertype += " | " + str(utiliy_id.code)
                        # if lmrvalue:
                        #     lmrvalue += " | " + str(
                        #         line[2]['start_reading_value'])
                        if not emetertype:
                            if utiliy_id:
                                emetertype = str(utiliy_id.code)
                        if 'start_reading_value' in line[2]:
                            if lmrvalue:
                                lmrvalue += " | " + str(
                                    line[2]['start_reading_value'])
                            else:
                                lmrvalue = str(line[2]['start_reading_value'])
                        if 'start_date' in line[2]:
                            lmrdate = line[2]['start_date']

                dupes = [x for n, x in enumerate(ldata) if x in ldata[:n]]
                if dupes:
                    raise UserError(
                        _("Plese can not set duplicate supply sourec type."))
                else:
                    if 'utilities_no' in values:
                        fac_ids = self.search([('utilities_no', '=',
                                                values['utilities_no'])])
                        if fac_ids:
                            for fid in fac_ids:
                                if fid.facilities_line:
                                    for fl in fid.facilities_line:
                                        if fl.source_type_id.id in ldata:
                                            raise UserError(
                                                _("Plese can not set duplicate supply sourec type."
                                                  ))
        if emetertype:
            values['e_meter_type'] = emetertype
        if lmrvalue:
            values['lmr_value'] = lmrvalue
        if lmrdate:
            values['lmr_date'] = lmrdate
        result = super(PMSFacilities, self).write(values)

        return result

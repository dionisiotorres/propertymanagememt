# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from odoo.addons.property_management_system.models import api_rauth_config


class PMSFacilities(models.Model):
    _name = 'pms.facilities'
    _description = "Facilities"

    name = fields.Char(default="New",
                       related='meter_no.name',
                       readonly=True,
                       store=True,
                       required=True,
                       track_visibility=True)
    utility_type_id = fields.Many2one('pms.utility.supply.type',
                                      "Utility Supply Type",
                                      required=True,
                                      track_visibility=True)
    meter_no = fields.Many2one("pms.equipment",
                               "Meter No",
                               required=True,
                               track_visibility=True)
    interface_type = fields.Selection([('auto', 'Auto'), ('manual', 'Manual'),
                                       ('mobile', 'Mobile')],
                                      "Interface Type",
                                      track_visibility=True)
    remark = fields.Text("Remark", track_visibility=True)
    status = fields.Boolean("Status", default=True, track_visibility=True)
    facilities_line = fields.One2many("pms.facility.lines",
                                      "facility_id",
                                      "Facility Lines",
                                      track_visibility=True)
    property_id = fields.Many2one("pms.properties",
                                  "Property",
                                  required=True,
                                  track_visibility=True)
    count_unit = fields.Integer("Count Unit", compute="_get_count_unit")
    install_date = fields.Date("Install Date", track_visibility=True)

    # _sql_constraints = [('name_unique', 'unique(name)',
    #                      'Your name is exiting in the database.')]

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
        id = super(PMSFacilities, self).create(values)
        if id:
            property_obj = self.env['pms.properties'].browse(
                values['property_id'])
            integ_obj = self.env['pms.api.integration']
            api_type_obj = self.env['pms.api.type'].search([
                ('name', '=', "SpaceUnitFacility")
            ])
            datas = api_rauth_config.APIData(id, values, property_obj,
                                             integ_obj, api_type_obj)
        return id
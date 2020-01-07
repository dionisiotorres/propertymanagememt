# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools


class PMSEquipment(models.Model):
    _name = 'pms.equipment'
    _description = "Equipments"

    equipment_type_id = fields.Many2one("pms.equipment.type",
                                        string="Equipment Type",
                                        track_visibility=True,
                                        required=True)
    name = fields.Char("Serial No", required=True, track_visibility=True)
    model = fields.Char("Model", required=True, track_visibility=True)
    manufacutrue = fields.Char("Manufacture", track_visibility=True)
    ref_code = fields.Char("RefCode", track_visibility=True)
    # active = fields.Boolean(default=True, track_visibility=True)
    property_id = fields.Many2one("pms.properties",
                                  "Property",
                                  required=True,
                                  track_visibility=True)
    digit = fields.Integer("Digit", track_visibility=True)
    count_facility = fields.Integer("Count Unit",
                                    compute="_get_count_facility")
    roll_over_type = fields.Selection([('normal', 'Normal'),
                                       ('kwtomw', 'KW to MW')],
                                      "Rollover Type")
    _sql_constraints = [('name_unique', 'unique(name)',
                         'Your name is exiting in the database.')]

    @api.multi
    def _get_count_facility(self):
        count = 0
        unit_ids = self.env['pms.facilities'].search([('meter_no', '=',
                                                       self.id),
                                                      ('status', '=', True)])
        for unit in unit_ids:
            self.count_facility += 1

    @api.multi
    def action_facilities(self):
        facility_ids = self.env['pms.facilities'].search([
            ('meter_no', '=', self.id), ('status', '=', True)
        ])

        action = self.env.ref(
            'property_management_system.action_facilities_all').read()[0]
        if len(facility_ids) > 1:
            action['domain'] = [('id', 'in', facility_ids.ids)]
        elif len(facility_ids) == 1:
            action['views'] = [(self.env.ref(
                'property_management_system.view_facilities_form').id, 'form')]
            action['res_id'] = facility_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


class PMSEquipmentType(models.Model):
    _name = 'pms.equipment.type'
    _description = 'Equipment Types'

    name = fields.Char("Equipment Type", required=True, track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)

    _sql_constraints = [('name_unique', 'unique(name)',
                         'Your name is exiting in the database.')]
# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError


class PMSEquipment(models.Model):
    _name = 'pms.equipment'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Equipments"

    def _get_name(self):
        return self.name

    def _get_property(self):
        return self.env.user.current_property_id

    equipment_type_id = fields.Many2one("pms.equipment.type",
                                        string="Equipment Type",
                                        track_visibility=True,
                                        required=True)
    name = fields.Char("Serial No",
                       required=True,
                       track_visibility=True,
                       help='Serial No of Equipment')
    model = fields.Char("Model",
                        required=True,
                        track_visibility=True,
                        help='Model of Equipment.')
    manufacturer = fields.Char("Manufacturer", track_visibility=True)
    ref_code = fields.Char("Reference Code", track_visibility=True)
    property_id = fields.Many2one("pms.properties",
                                  "Property",
                                  default=_get_property,
                                  required=True,
                                  track_visibility=True)
    digit = fields.Integer(
        "Digit",
        track_visibility=True,
        help='The maximun capicity to display on equipment screen(esp. meter)')
    count_facility = fields.Integer("Count Unit",
                                    compute="_get_count_facility")
    roll_over_type = fields.Selection(
        [('DIGITROLLOVER', 'Digit RollOver'),
         ('UNITROLLOVER', 'Unit RollOver'),
         ('CURRENTROLLOVER', 'Current RollOver')],
        "Rollover Type",
        help='Which method will be use if equipment roll over.')
    utilities_type = fields.Many2one("pms.utilities.type", "Utiliteis Type")
    utilities_code = fields.Char("Utiliteis Code",
                                 related="utilities_type.code")
    current_unit_type = fields.Selection([('watt', "Watts"),
                                          ('kilowatt', "Kilowatts"),
                                          ('megawatt', "Megawatts")],
                                         string="Current Unit Type")
    meter_type = fields.Selection([('normal', 'Normal'),
                                   ('share-meter', 'Share Meter')],
                                  string="Meter Type")
    power_system = fields.Selection([('single-phase', 'Single Phase'),
                                     ('three-phase', 'Three Phase')],
                                    string="Power System")
    meter_template_id = fields.Many2one("pms.meter.template",
                                        "Meter Templates")
    equipment_line = fields.One2many("pms.equipment.line",
                                     "equipment_id",
                                     string="Equipment Lines")

    @api.multi
    def _get_count_facility(self):
        count = 0
        unit_ids = self.env['pms.facilities'].search([('utilities_no', '=',
                                                       self.id),
                                                      ('inuse', '=', True)])
        for unit in unit_ids:
            self.count_facility += 1

    @api.multi
    def action_facilities(self):
        facility_ids = self.env['pms.facilities'].search([
            ('utilities_no', '=', self.id), ('status', '=', True)
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

    @api.model
    def create(self, values):
        equip_id = self.search([('name', '=', values['name'])])
        if equip_id:
            raise UserError(_("%s is already existed" % values['name']))
        return super(PMSEquipment, self).create(values)

    @api.multi
    def write(self, vals):
        if 'name' in vals:
            equip_id = self.search([('name', '=', vals['name'])])
            if equip_id:
                raise UserError(_("%s is already existed" % vals['name']))
        return super(PMSEquipment, self).write(vals)

    def _compute_line_data_for_template_change(self, line):
        return {'utilities_supply_id': line.utilities_supply_id.id}

    @api.onchange('meter_template_id')
    def onchange_meter_template_id(self):
        template = self.meter_template_id.with_context(
            lang=self._context.get('lang'))
        equipment_lines = [(5, 0, 0)]
        data = []
        if template:
            if len(template.template_line) > 0:
                for l in template.template_line:
                    data = self._compute_line_data_for_template_change(l)
                    equipment_lines.append((0, 0, data))
                    self.equipment_line = equipment_lines
            self.utilities_type = template.utilities_type
            self.current_unit_type = template.current_unit_type
            self.meter_type = template.meter_type
            self.power_system = template.power_system
            self.digit = template.digit

    @api.onchange('digit')
    def onchange_digit(self):
        if self.digit and self.name:
            facility_id = self.env['pms.facilities'].search([
                ('utilities_no', '=', self.name), ('inuse', '=', True)
            ])
            if facility_id.facilities_line:
                for fl in facility_id.facilities_line:
                    spunitfl_ids = self.env[
                        'pms.space.unit.facility.lines'].search([
                            ('facility_id', '=', facility_id.id),
                            ('facility_line_id', '=', fl.id),
                            ('inuse', '=', True)
                        ])
                    spunitfl_ids.write({'digit': self.digit})


class PMSEquipmentType(models.Model):
    _name = 'pms.equipment.type'
    _description = 'Equipment Types'
    _order = 'sequence,name'

    name = fields.Char("Equipment Type", required=True, track_visibility=True)
    description = fields.Text("Description", track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)
    sequence = fields.Integer(track_visibility=True)
    index = fields.Integer(compute='_compute_index')

    @api.one
    def _compute_index(self):
        cr, uid, ctx = self.env.args
        self.index = self._model.search_count(
            cr, uid, [('sequence', '<', self.sequence)], context=ctx) + 1

    @api.model
    def create(self, values):
        equip_type_id = self.search([('name', '=', values['name'])])
        if equip_type_id:
            raise UserError(_("%s is already existed" % values['name']))
        return super(PMSEquipmentType, self).create(values)

    @api.multi
    def write(self, vals):
        if 'name' in vals:
            equip_type_id = self.search([('name', '=', vals['name'])])
            if equip_type_id:
                raise UserError(_("%s is already existed" % vals['name']))
        return super(PMSEquipmentType, self).write(vals)


class PMSEquipmentLine(models.Model):
    _name = 'pms.equipment.line'
    _description = 'Equipment Lines'

    utilities_supply_id = fields.Many2one("pms.utilities.supply",
                                          "Utilities Supply")
    equipment_id = fields.Many2one("pms.equipment", "Equipment")
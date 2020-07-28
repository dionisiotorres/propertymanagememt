# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PMSMeterTemplate(models.Model):
    _name = 'pms.meter.template'
    _description = "Meter Template"
    _order = 'sequence,name'

    name = fields.Char("Name")
    utilities_type = fields.Many2one("pms.utilities.type","Utiliteis Type")
    power_system = fields.Selection([('single-phase','Single Phase'),('three-phase','Three Phase')],string="Power System")
    meter_type = fields.Selection([('normal','Normal'),('share-meter','Share Meter')],string="Meter Type")
    current_unit_type = fields.Selection([('watt',"Watts"),('kilowatt',"Kilowatts"),('megawatt',"Megawatts")],string="Current Unit Type")
    digit = fields.Integer(
        "Digit",
        track_visibility=True,
        help='The maximun capicity to display on equipment screen(esp. meter)')
    template_line = fields.One2many("pms.meter.template.line","template_id",string="Template Lines")
    sequence = fields.Integer(track_visibility=True)
    index = fields.Integer(compute='_compute_index')
    _sql_constraints = [('name_unique', 'unique(name)',
                         'Template Name is already existed.')]

    @api.one
    def _compute_index(self):
        cr, uid, ctx = self.env.args
        self.index = self._model.search_count(cr,uid,[('sequence','<',self.sequence)],context=ctx) + 1

class PMSMeterTemplateLine(models.Model):
    _name = 'pms.meter.template.line'
    _description = "Meter Template Line"

    utilities_supply_id = fields.Many2one("pms.utilities.supply","Utilities Supply")
    template_id = fields.Many2one("pms.meter.template", "Meter Template")


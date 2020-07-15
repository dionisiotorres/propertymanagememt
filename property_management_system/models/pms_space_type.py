from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError


class PMSSpaceType(models.Model):
    _name = 'pms.space.type'
    _description = 'Space Type'
    _order = 'sequence,name'

    name = fields.Char("Space Type", required=True, track_visibility=True)
    code = fields.Char("Space Code", required=True, track_visibility=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(track_visibility=True)
    index = fields.Integer(compute='_compute_index')
    is_import = fields.Boolean("Is Import?")

    @api.one
    def _compute_index(self):
        cr, uid, ctx = self.env.args
        self.index = self._model.search_count(cr,uid,[('sequence','<',self.sequence)],context=ctx) + 1

    @api.multi
    def toggle_active(self):
        for pt in self:
            if not pt.active:
                pt.active = self.active
        super(PMSSpaceType, self).toggle_active()

    @api.model
    def create(self, values):
        equip_id = self.search([('name', '=', values['name'])])
        if equip_id:
            raise UserError(_("%s is already existed" % values['name']))
        return super(PMSSpaceType, self).create(values)

    @api.multi
    def write(self, vals):
        if 'name' in vals:
            equip_id = self.search([('name', '=', vals['name'])])
            if equip_id:
                raise UserError(_("%s is already existed" % vals['name']))
        return super(PMSSpaceType, self).write(vals)

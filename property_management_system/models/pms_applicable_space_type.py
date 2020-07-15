from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError


class PMSApplicableSpaceType(models.Model):
    _name = 'pms.applicable.space.type'
    _description = 'Applicable Space Type'
    _order = 'sequence,name'

    name = fields.Char("Space Type", required=True, track_visibility=True)
    space_type_id = fields.Many2one("pms.space.type",
                                    "Main Space Type",
                                    required=True)
    chargeable = fields.Boolean("Chargable", default=True, track_visibility=True)
    divisible = fields.Boolean("Merge-Split", default=True, track_visibility=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(track_visibility=True)
    index = fields.Integer(compute='_compute_index')

    @api.one
    def _compute_index(self):
        cr, uid, ctx = self.env.args
        self.index = self._model.search_count(cr,uid,[('sequence','<',self.sequence)],context=ctx) + 1

    @api.multi
    def toggle_active(self):
        for pt in self:
            if not pt.active:
                pt.active = self.active
        super(PMSTerms, self).toggle_active()

    @api.model
    def create(self, values):
        charge_type_id = self.search([('name', '=', values['name'])])
        if charge_type_id:
            raise UserError(_("%s is already existed" % values['name']))
        return super(PMSApplicableSpaceType, self).create(values)

    @api.multi
    def write(self, vals):
        if 'name' in vals:
            charge_type_id = self.search([('name', '=', vals['name'])])
            if charge_type_id:
                raise UserError(_("%s is already existed" % vals['name']))
        return super(PMSApplicableSpaceType, self).write(vals)
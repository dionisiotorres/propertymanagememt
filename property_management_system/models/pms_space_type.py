from odoo import models, fields, api


class PMSSpaceType(models.Model):
    _name = 'pms.space.type'
    _description = 'Space Type'
    _order = 'ordinal_no,name'

    name = fields.Char("Space Type", required=True, track_visibility=True)
    ordinal_no = fields.Integer("Ordinal No", required=True)
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        for pt in self:
            if not pt.active:
                pt.active = self.active
        super(PMSSpaceType, self).toggle_active()

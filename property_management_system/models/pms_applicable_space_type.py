from odoo import models, fields, api


class PMSApplicableSpaceType(models.Model):
    _name = 'pms.applicable.space.type'
    _description = 'Applicable Space Type'

    name = fields.Char("Name", required=True, track_visibility=True)
    space_type = fields.Many2one("pms.space.type", "Type", required=True)
    chargeable = fields.Boolean("Chargeable", track_visibility=True)
    divisible = fields.Boolean("Divisible", track_visibility=True)
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        for pt in self:
            if not pt.active:
                pt.active = self.active
        super(PMSTerms, self).toggle_active()
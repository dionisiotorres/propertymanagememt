from odoo import models, fields, api


class PMSApplicableSpaceType(models.Model):
    _name = 'pms.applicable.space.type'
    _description = 'Applicable Space Type'
    _order = 'ordinal_no,name'

    name = fields.Char("Space Type", required=True, track_visibility=True)
    space_type_id = fields.Many2one("pms.space.type",
                                    "Main Space Type",
                                    required=True)
    chargeable = fields.Boolean("IsChargable", track_visibility=True)
    divisible = fields.Boolean("Can be divided", track_visibility=True)
    ordinal_no = fields.Integer("Ordinal No",
                                required=True,
                                help='To display order as prefer')
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        for pt in self:
            if not pt.active:
                pt.active = self.active
        super(PMSTerms, self).toggle_active()
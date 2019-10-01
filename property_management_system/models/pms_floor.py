from odoo import models, fields, api, tools, _
import base64


class PMSFloor(models.Model):
    _name = 'pms.floor'
    _description = "PMS Floor"
    _order = "code,name"

    name = fields.Char("Description", required=True)
    code = fields.Char("Floor Code")
    floor_code_ref = fields.Char("Floor Ref Code")
    active = fields.Boolean("Active", default=True)
    _sql_constraints = [
        ('name_unique', 'unique(name,code)',
         'Please add other name/code that is exiting in the database.')
    ]

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.code
            result.append((record.id, code))
        return result

    @api.multi
    def toggle_active(self):
        for pt in self:
            if not pt.active:
                pt.active = self.active
        super(PMSFloor, self).toggle_active()
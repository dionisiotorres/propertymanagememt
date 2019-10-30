import base64
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError


class PMSFloor(models.Model):
    _name = 'pms.floor'
    _description = "PMS Floor"
    _order = "code,name"

    name = fields.Char("Description", required=True)
    code = fields.Char("Floor Code")
    floor_code_ref = fields.Char("Floor Ref Code")
    active = fields.Boolean("Active", default=True)
    _sql_constraints = [
        ('name_unique', 'unique(name)',
         'Please add other name that is exiting in the database.'),
        ('code_unique', 'unique(code)',
         'Please add other code that is exiting in the database.')
    ]

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.code
            result.append((record.id, code))
        return result

    @api.multi
    @api.onchange('code')
    def onchange_code(self):
        length = 0
        if self.code:
            length = len(self.code)
        if self.env.user.company_id.floor_code_len:
            if length > self.env.user.company_id.floor_code_len:
                raise UserError(
                    _("Please set your code length less than %s." %
                      (self.env.user.company_id.floor_code_len)))

    @api.multi
    def toggle_active(self):
        for pt in self:
            if not pt.active:
                pt.active = self.active
        super(PMSFloor, self).toggle_active()

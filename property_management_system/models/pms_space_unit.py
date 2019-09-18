from odoo import models, fields, api, tools


class PMSSpaceUnit(models.Model):
    _name = 'pms.space.unit'
    _description = "Space Units"
    _order = "parent_id"

    name = fields.Char("Unit No",
                       compute='get_unit_no',
                       store=True,
                       readonly=True)
    property_id = fields.Many2one("pms.properties",
                                  string="Property",
                                  required=True)
    floor_id = fields.Many2one("pms.floor", string="Floor", required=True)
    floor_code = fields.Char(string="Floor Code",
                             related="floor_id.code",
                             store=False)
    unit_no = fields.Char("Space Unit No", store=True, required=True)
    parent_id = fields.Many2one("pms.space.unit", "Parent", store=True)
    unittype_id = fields.Many2one("pms.space.type", "Space Type")
    uom = fields.Many2one("pms.uom", "UOM")
    area = fields.Integer("Area")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    status = fields.Selection([('vacant', 'Vacant'), ('occupied', 'Occupied')],
                              string="Status",
                              default="vacant")
    remark = fields.Text("Remark")

    # utility_id = fields.One2many("pms.space.utility", "unit_id", "Facility")
    _sql_constraints = [('name_unique', 'unique(name)',
                         'Your Name is exiting in the database.')]

    @api.depends('unit_no', 'floor_code')
    def get_unit_no(self):
        if not self.floor_id and not self.unit_no:
            self.name = "New"
        if self.floor_id and not self.unit_no:
            self.name = self.floor_id.code
        if self.unit_no and not self.floor_id:
            self.name = self.unit_no
        if self.floor_id and self.unit_no:
            self.name = self.floor_id.code + "-" + self.unit_no

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.name
            result.append((record.id, code))
        return result

    @api.model
    def create(self, values):
        return super(PMSSpaceUnit, self).create(values)

    @api.multi
    def write(self, val):
        return super(PMSSpaceUnit, self).write(val)
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError


class PMSSpaceUnit(models.Model):
    _name = 'pms.space.unit'
    _description = "Space Units"
    _order = "parent_id"

    def get_floor(self):
        if not self.floor_id:
            floor_ids = self.env['pms.floor'].search([], order='id asc')
            if floor_ids:
                floor_id = floor_ids[0]
                return floor_id
            else:
                val = {
                    'name': 'Floor 1',
                    'code': 'F1',
                    'floor_code_ref': '01',
                    'active': True
                }
                floor = self.env['pms.floor'].create(val)
                return floor

    name = fields.Char("Unit No",
                       compute='get_unit_no',
                       store=True,
                       readonly=True)
    unit_code = fields.Char("Unit",
                            compute='get_unit_no',
                            store=True,
                            readonly=True)
    property_id = fields.Many2one("pms.properties",
                                  string="Property",
                                  required=True)
    floor_id = fields.Many2one("pms.floor",
                               string="Floor",
                               default=get_floor,
                               required=True)
    floor_code = fields.Char(string="Floor Code",
                             related="floor_id.code",
                             store=False)
    unit_no = fields.Char("Space Unit No", store=True, required=True)
    parent_id = fields.Many2one("pms.space.unit", "Parent", store=True)
    unittype_id = fields.Many2one("pms.space.type", "Space Type")
    uom = fields.Many2one("uom.uom", "UOM")
    area = fields.Integer("Area")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    status = fields.Selection([('vacant', 'Vacant'), ('occupied', 'Occupied')],
                              string="Status",
                              default="vacant")
    rate = fields.Float("Rate")
    remark = fields.Text("Remark")

    facility_line = fields.Many2many("pms.facilities", "pms_unit_facility_rel",
                                     "unit_id", "facilities_id",
                                     "Facility Lines")
    _sql_constraints = [('name_unique', 'unique(name)',
                         'Your Name is exiting in the database.')]

    @api.one
    @api.depends('unit_no', 'floor_id', 'property_id')
    def get_unit_no(self):
        if self.env.user.company_id.space_unit_code_format:
            format_ids = self.env['pms.format.detail'].search(
                [('format_id', '=',
                  self.env.user.company_id.space_unit_code_format.id)],
                order='position_order asc')
            val = []
            for fid in format_ids:
                if fid.value_type == 'dynamic':
                    if self.floor_id.code and fid.dynamic_value == 'floor code':
                        val.append(self.floor_id.code)
                    if self.floor_id.floor_code_ref and fid.dynamic_value == 'floor ref code':
                        val.append(self.floor_id.floor_code_ref)
                    if self.property_id.code and fid.dynamic_value == 'property code':
                        val.append(self.property_id.code)
                if fid.value_type == 'fix':
                    if self.unit_no or self.floor_id:
                        val.append(fid.fix_value)
                if fid.value_type == 'digit':
                    if self.unit_no and len(self.unit_no) > fid.digit_value:
                        raise UserError(
                            _("Please Unit Length less than your format digit."
                              ))
                if fid.value_type == 'datetime':
                    val.append(fid.datetime_value)
            space = []
            self.name = ''
            self.unit_code = ''
            if len(val) > 0:
                for l in range(len(val)):
                    self.name += str(val[l])
                    self.unit_code += str(val[l])
                if self.unit_no:
                    self.name += str(self.unit_no)

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

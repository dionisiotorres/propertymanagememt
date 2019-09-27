from odoo import fields, models, api, _


class PmsFormat(models.Model):
    _name = "pms.format"
    _description = "Property Formats"
    _order = "name"

    name = fields.Char("Name")
    sample = fields.Char("Sample",
                         compute='get_sample_format',
                         store=True,
                         readonly=True)
    active = fields.Boolean(default=True)
    format_line_id = fields.One2many("pms.format.detail", "format_id",
                                     "Format Line")

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.name
            result.append((record.id, code))
        return result

    @api.model
    def create(self, values):
        return super(PmsFormat, self).create(values)

    @api.multi
    @api.depends('format_line_id')
    def get_sample_format(self):
        f_val = []
        self.sample = ''
        if self.format_line_id:
            for fl in self.mapped('format_line_id'):
                if fl.value_type == 'fix' and fl.fix_value:
                    f_val.append(fl.fix_value)
                if fl.value_type == 'digit' and fl.digit_value:
                    for d in range(fl.digit_value):
                        f_val.append(str('x'))
                if fl.value_type == 'dynamic' and fl.dynamic_value:
                    f_val.append(fl.dynamic_value)
                if fl.value_type == 'datetime' and fl.datetime_value:
                    f_val.append(fl.datetime_value)
            if f_val:
                for sm in range(len(f_val)):
                    self.sample += f_val[sm]

    @api.multi
    def toggle_active(self):
        for pt in self:
            if not pt.active:
                pt.active = self.active
        super(PmsFormat, self).toggle_active()


class PmsFormatDetail(models.Model):
    _name = "pms.format.detail"
    _description = "Property Formats Details"
    _order = "name"

    @api.one
    @api.depends('fix_value', 'digit_value', 'dynamic_value', 'datetime_value')
    def get_value_type(self):
        if self.value_type:
            if self.value_type == 'fix':
                self.value = self.fix_value
            if self.value_type == 'dynamic':
                self.value = self.dynamic_value
            if self.value_type == 'digit':
                self.value = self.digit_value
            if self.value_type == 'datetime':
                self.value = self.datetime_value

    name = fields.Char("Name", default="New")
    format_id = fields.Many2one("pms.format", "Format")
    position_order = fields.Integer("Position Order")
    value_type = fields.Selection([('fix', "Fix"), ('dynamic', 'Dynamic'),
                                   ('digit', 'Digit'),
                                   ('datetime', 'Datetime')],
                                  string="Type",
                                  default="")
    fix_value = fields.Char("Fixed Value", store=True)
    digit_value = fields.Integer("Digit Value", store=True)
    dynamic_value = fields.Selection([('unit code', 'unit code'),
                                      ('property code', 'property code'),
                                      ('pos code', 'pos code'),
                                      ('floor code', 'floor code')],
                                     string="Dynamic Value",
                                     store=True)
    datetime_value = fields.Selection([('mmyy', 'MMYY'), ('mmyyyy', 'MMYYYY'),
                                       ('yy', 'YY'), ('yyyy', 'YYYY')],
                                      string="Date Value",
                                      store=True)
    value = fields.Char("Value", compute='get_value_type')


class Company(models.Model):
    _inherit = "res.company"

    property_id = fields.Many2one("pms.properties", "Property")
    property_code_len = fields.Integer("Property Code Length")
    floor_code_len = fields.Integer('Floor Code Length')
    space_unit_code_len = fields.Integer('Space Unit Code Length')
    space_unit_code_format = fields.Many2one('pms.format', 'Space Unit Format')
    pos_id_format = fields.Many2one('pms.format', 'POS ID Format')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def get_company_id(self):
        if not self.company_id:
            return self.env.user.company_id

    company_id = fields.Many2one('res.company', default=get_company_id)
    property_code_len = fields.Integer("Property Code Length",
                                       related="company_id.property_code_len",
                                       readonly=False)
    floor_code_len = fields.Integer('Floor Code Length',
                                    related='company_id.floor_code_len',
                                    readonly=False)
    space_unit_code_len = fields.Integer(
        'Space Unit Code Length',
        related="company_id.space_unit_code_len",
        readonly=False)
    space_unit_code_format = fields.Many2one(
        'pms.format',
        'Space Unit Format',
        related="company_id.space_unit_code_format",
        readonly=False)
    pos_id_format = fields.Many2one('pms.format',
                                    'POS ID Format',
                                    related="company_id.pos_id_format",
                                    readonly=False)

    @api.onchange('property_code_len')
    def onchange_property_code_len(self):
        if self.property_code_len:
            self.company_id.property_code_len = self.property_code_len

    @api.onchange('floor_code_len')
    def onchange_floor_code_len(self):
        if self.floor_code_len:
            self.company_id.floor_code_len = self.floor_code_len

    @api.onchange('space_unit_code_len')
    def onchange_space_unit_code_len(self):
        if self.space_unit_code_len:
            self.company_id.space_unit_code_len = self.space_unit_code_len

    @api.onchange('space_unit_code_format')
    def onchange_space_unit_code_format(self):
        if self.space_unit_code_format:
            self.company_id.space_unit_code_format = self.space_unit_code_format

    @api.onchange('pos_id_format')
    def onchange_pos_id_format(self):
        if self.pos_id_format:
            self.company_id.pos_id_format = self.pos_id_format

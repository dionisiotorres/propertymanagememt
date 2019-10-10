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
    _order = "position_order"

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
    # autogenerate = fields.Boolean("Auto Generate?")
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
                                      ('floor code', 'floor code'),
                                      ('floor ref code', 'floor ref code')],
                                     string="Dynamic Value",
                                     store=True)
    datetime_value = fields.Selection([('MM', 'MM'), ('MMM', 'MMM'),
                                       ('YY', 'YY'), ('YYYY', 'YYYY')],
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
    new_lease_term = fields.Many2one('pms.leaseterms',
                                     string="Add New Lease Term")
    extend_lease_term = fields.Many2one('pms.leaseterms',
                                        string="Extened Lease Term")
    # terminate_lease_term = fields.Many2one(
    #     'pms.leaseterms',
    #     string="Terminate Lease Term",
    # )
    lease_agre_format_id = fields.Many2one('pms.format',
                                           'Lease Agreement Format')
    rentschedule_type = fields.Selection(
        [('probation', "Probation"), ('calendar', "Calendar")],
        default='probation',
        string="Rent Schedule Type",
    )
    extend_count = fields.Integer("Extend count")
    pre_notice_terminate_term = fields.Integer("Pre-Terminate Terms(Days)")


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
                                    readonly=False,
                                    required=False)
    new_lease_term = fields.Many2one('pms.leaseterms',
                                     string="Add New Lease Term",
                                     related="company_id.new_lease_term",
                                     readonly=False,
                                     required=False)
    extend_lease_term = fields.Many2one('pms.leaseterms',
                                        string="Extened Lease Term",
                                        related="company_id.extend_lease_term",
                                        readonly=False,
                                        required=False)
    # terminate_lease_term = fields.Many2one(
    #     'pms.leaseterms',
    #     string="Terminate Lease Term",
    #     related="company_id.terminate_lease_term",
    #     readonly=False,
    #     required=False)
    lease_agre_format_id = fields.Many2one(
        'pms.format',
        'Lease Format',
        related="company_id.lease_agre_format_id",
        readonly=False)
    rentschedule_type = fields.Selection(
        [('probation', "Probation"), ('calendar', "Calendar")],
        string="Rent Schedule",
        related="company_id.rentschedule_type",
        readonly=False)
    extend_count = fields.Integer("Extend count",
                                  related="company_id.extend_count",
                                  readonly=False)
    pre_notice_terminate_term = fields.Integer(
        "Pre-Terminate Terms(Days)",
        related="company_id.pre_notice_terminate_term",
        readonly=False)

    @api.onchange('pre_notice_terminate_term')
    def onchange_pre_notice_terminate_term(self):
        if self.pre_notice_terminate_term:
            self.company_id.pre_notice_terminate_term = self.pre_notice_terminate_term

    @api.onchange('extend_count')
    def onchange_extend_count(self):
        if self.extend_count:
            self.company_id.extend_count = self.extend_count

    @api.onchange('rentschedule_type')
    def onchange_rentschedule_type(self):
        if self.rentschedule_type:
            self.company_id.rentschedule_type = self.rentschedule_type

    @api.onchange('new_lease_term')
    def onchange_new_lease_term(self):
        if self.new_lease_term:
            self.company_id.new_lease_term = self.new_lease_term

    @api.onchange('extend_lease_term')
    def onchange_extend_lease_term(self):
        if self.extend_lease_term:
            self.company_id.extend_lease_term = self.extend_lease_term

    # @api.onchange('terminate_lease_term')
    # def onchange_terminate_lease_term(self):
    #     if self.terminate_lease_term:
    #         self.company_id.terminate_lease_term = self.terminate_lease_term

    @api.onchange('lease_agre_format_id')
    def onchange_lease_agre_format_id(self):
        if self.lease_agre_format_id:
            self.company_id.lease_agre_format_id = self.lease_agre_format_id

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


class PMSLeaseTerms(models.Model):
    _name = 'pms.leaseterms'
    _description = "Property LeaseTerms"
    _order = "name"

    name = fields.Char("Description", required=True)
    lease_period_type = fields.Selection([('month', "Month"),
                                          ('year', "Year")],
                                         string="Lease Period Type")
    min_time_period = fields.Integer("Min Time Period")
    max_time_period = fields.Integer("Max Time Period")
    # extend_count = fields.Integer("Extend count")
    extend_period = fields.Integer("Notice Period(mon)")
    active = fields.Boolean("Active", default=True)

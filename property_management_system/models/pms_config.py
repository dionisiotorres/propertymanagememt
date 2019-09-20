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
                    f_val.append(fl.fix_value + '/')
                if fl.value_type == 'digit' and fl.digit_value:
                    f_val.append(str(fl.digit_value) + '/')
                if fl.value_type == 'dynamic' and fl.dynamic_value:
                    f_val.append(fl.dynamic_value + '/')
                if fl.value_type == 'datetime' and fl.datetime_value:
                    f_val.append(fl.datetime_value + '/')
            if f_val:
                for sm in range(len(f_val)):
                    if len(f_val) - 1 == sm:
                        f_val[sm]
                        self.sample += f_val[sm].split('/')[0]
                    else:
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

    name = fields.Char("Name", default="New")
    format_id = fields.Many2one("pms.format", "Format")
    position_order = fields.Integer("Position Order")
    value_type = fields.Selection([('fix', "Fix"), ('dynamic', 'Dynamic'),
                                   ('digit', 'Digit'),
                                   ('datetime', 'Datetime')],
                                  string="Type",
                                  default="")
    fix_value = fields.Char("Fixed Value",
                            compute="get_value_type",
                            store=True)
    digit_value = fields.Integer("Digit Value",
                                 compute="get_value_type",
                                 store=True)
    dynamic_value = fields.Char("Dynamic Value",
                                compute="get_value_type",
                                store=True)
    datetime_value = fields.Char("Date Value",
                                 compute="get_value_type",
                                 store=True)
    value = fields.Char("Value")

    @api.one
    @api.depends("value")
    def get_value_type(self):
        if self.value_type:
            if self.value_type == 'fix':
                self.fix_value = self.value
            if self.value_type == 'dynamic':
                self.dynamic_value = self.value
            if self.value_type == 'digit':
                self.digit_value = self.value
            if self.value_type == 'datetime':
                self.datetime_value = self.value


class Company(models.Model):
    _inherit = "res.company"

    property_code_len = fields.Integer("Property Code Length")
    floor_code_len = fields.Integer('Floor Code Length')
    space_unit_code_len = fields.Integer('Space Unit Code Length')
    space_unit_code_format = fields.Many2one('pms.format', 'Space Unit Format')
    pos_id_format = fields.Many2one('pms.format', 'POS ID Format')


class PMSRule(models.TransientModel):
    _name = 'pms.rule'
    _description = "Rule"

    @api.model
    def _get_default_company(self):
        if not self.company_id:
            return self.env.user.company_id

    @api.model
    def _get_default_property_code_len(self):
        if self.env.user.company_id:
            rule_id = self.env['pms.rule'].search([
                ('company_id', '=', self.env.user.company_id.id)
            ])
            if rule_id:
                return rule_id.property_code_len

    @api.model
    def _get_default_floor_code_len(self):
        if self.env.user.company_id:
            rule_id = self.env['pms.rule'].search([
                ('company_id', '=', self.env.user.company_id.id)
            ])
            if rule_id:
                return rule_id.floor_code_len

    @api.model
    def _get_default_space_unit_code_len(self):
        if self.env.user.company_id:
            rule_id = self.env['pms.rule'].search([
                ('company_id', '=', self.env.user.company_id.id)
            ])
            if rule_id:
                return rule_id.space_unit_code_len

    @api.model
    def _get_default_space_unit_code_format(self):
        if self.env.user.company_id:
            rule_id = self.env['pms.rule'].search([
                ('company_id', '=', self.env.user.company_id.id)
            ])
            if rule_id:
                return rule_id.space_unit_code_format

    @api.model
    def _get_default_pos_id_format(self):
        if self.env.user.company_id:
            rule_id = self.env['pms.rule'].search([
                ('company_id', '=', self.env.user.company_id.id)
            ])
            if rule_id:
                return rule_id.pos_id_format

    name = fields.Char("Setting")
    company_id = fields.Many2one("res.company",
                                 "Company",
                                 default=_get_default_company)
    property_code_len = fields.Integer("Property Code Length",
                                       default=_get_default_property_code_len)
    floor_code_len = fields.Integer('Floor Code Length',
                                    default=_get_default_floor_code_len)
    space_unit_code_len = fields.Integer(
        'Space Unit Code Length', default=_get_default_space_unit_code_len)
    space_unit_code_format = fields.Many2one(
        'pms.format',
        'Space Unit Format',
        default=_get_default_space_unit_code_format)
    pos_id_format = fields.Many2one('pms.format',
                                    'POS ID Format',
                                    default=_get_default_pos_id_format)


class PMSRuleSetting(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'pms.rule.setting'
    _inherit = 'pms.rule'

    @api.multi
    def copy(self, values):
        raise UserError(_("Cannot duplicate configuration!"), "")

    @api.multi
    def execute(self):
        vals = {}
        self.ensure_one()
        rule_id = self.env['pms.rule'].search([])
        vals = {
            'name': _("Setting"),
            'company_id': self.company_id.id,
            'property_code_len': self.property_code_len,
            'floor_code_len': self.floor_code_len,
            'space_unit_code_len': self.space_unit_code_len,
            'space_unit_code_format': self.space_unit_code_format.id,
            'pos_id_format': self.pos_id_format.id,
        }
        if rule_id:
            rule_id.write(vals)
        else:
            self.env['pms.rule'].create(vals)
        return {
            'type': 'ir.actions.client',
            'name': _('Setting'),
            'res_model': 'pms.rule',
            'tag': 'reload',
        }
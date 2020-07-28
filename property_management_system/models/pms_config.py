from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError


class PmsFormat(models.Model):
    _name = "pms.format"
    _description = "Property Formats"
    _order = "name"

    name = fields.Char("Name", required=True)
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
            sample = record.sample
            result.append((record.id, sample))
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
                        f_val.append(str(d+1))
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

    @api.model
    def create(self, values):
        format_id = self.search([('name', '=', values['name'])])
        if format_id:
            raise UserError(_("%s is already existed" % values['name']))
        return super(PmsFormat, self).create(values)

    @api.multi
    def write(self, vals):
        format_id = None
        if 'name' in vals:
            sample_id = self.search([('name', '=', vals['name'])])
            if sample_id:
                raise UserError(_("%s is already existed" % vals['name']))
        return super(PmsFormat, self).write(vals)


class PmsFormatDetail(models.Model):
    _name = "pms.format.detail"
    _description = "Property Formats Details"
    _order = "sequence"

    @api.one
    @api.depends(
        'fix_value',
        'digit_value',
        'dynamic_value',
        'datetime_value',
    )
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
    # position_order = fields.Integer("Position Order",
    #                                 compute='_get_line_numbers',
    #                                 store=True,
    #                                 readonly=False)
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
    sequence = fields.Integer()
    index = fields.Integer(compute='_compute_index')

    @api.one
    def _compute_index(self):
        cr, uid, ctx = self.env.args
        self.index = self._model.search_count(cr,uid,[('sequence','<',self.sequence)],context=ctx) + 1


class Users(models.Model):
    _inherit = "res.users"

    # def _get_property(self):
    #     return self.env.user.property_id

    property_id = fields.Many2many("pms.properties",
                                   'property_id',
                                   'user_id',
                                   "pms_property_user_rel",
                                   "Property",
                                   store=True,
                                   track_visibility=True)

   
class UsersView(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, values):
        values = self._remove_reified_groups(values)
        user = super(UsersView, self).create(values)
        group_multi_company = self.env.ref('base.group_multi_company', False)
        if group_multi_company and 'company_ids' in values:
            if len(user.company_ids) <= 1 and user.id in group_multi_company.users.ids:
                user.write({'groups_id': [(3, group_multi_company.id)]})
            elif len(user.company_ids) > 1 and user.id not in group_multi_company.users.ids:
                user.write({'groups_id': [(4, group_multi_company.id)]})
        group_multi_property = self.env.ref('property_management_system.group_multi_property', False)
        if group_multi_property and 'property_id' in values:
            if len(user.property_id) <= 1 and user.id in group_multi_property.users.ids:
                user.write({'groups_id': [(3, group_multi_property.id)]})
            elif len(user.property_id) > 1 and user.id not in group_multi_property.users.ids:
                user.write({'groups_id': [(4, group_multi_property.id)]})
        return user

    @api.multi
    def write(self, values):
        values = self._remove_reified_groups(values)
        res = super(UsersView, self).write(values)
        group_multi_company = self.env.ref('base.group_multi_company', False)
        if group_multi_company and 'company_ids' in values:
            for user in self:
                if len(user.company_ids) <= 1 and user.id in group_multi_company.users.ids:
                    user.write({'groups_id': [(3, group_multi_company.id)]})
                elif len(user.company_ids) > 1 and user.id not in group_multi_company.users.ids:
                    user.write({'groups_id': [(4, group_multi_company.id)]})
        group_multi_property = self.env.ref('property_management_system.group_multi_property', False)
        if group_multi_property and 'property_id' in values:
            for user in self:
                if len(user.property_id) <= 1 and user.id in group_multi_property.users.ids:
                    user.write({'groups_id': [(3, group_multi_property.id)]})
                elif len(user.property_id) > 1 and user.id not in group_multi_property.users.ids:
                    user.write({'groups_id': [(4, group_multi_property.id)]})
        return res



class Company(models.Model):
    _inherit = "res.company"

    def _default_space_unit_format(self):
        if not self.pos_id_format:
            return self.env.ref('base.main_company').space_unit_code_format

    def _default_pos_id_format(self):
        if not self.pos_id_format:
            return self.env.ref('base.main_company').pos_id_format

    def _default_lease_agreement_format(self):
        if not self.lease_agre_format_id:
            return self.env.ref('base.main_company').lease_agre_format_id
    
    def _default_prospect_format(self):
        if not self.prospect_format_id:
            return self.env.ref('base.main_company').prospect_format_id

    def _default_new_lease_term(self):
        if not self.new_lease_term:
            return self.env.ref('base.main_company').new_lease_term

    def _default_lease_extend_term(self):
        if not self.extend_lease_term:
            return self.env.ref('base.main_company').extend_lease_term

    property_code_len = fields.Integer("Property Code Length",
                                       default=8,
                                       track_visibility=True)
    floor_code_len = fields.Integer('Floor Code Length',
                                    track_visibility=True,
                                    default=15)
    # space_unit_code_len = fields.Integer('Space Unit Code Length', default=30)
    space_unit_code_format = fields.Many2one(
        'pms.format',
        'Space Unit Format',
        default=_default_space_unit_format,
        track_visibility=True)
    pos_id_format = fields.Many2one('pms.format',
                                    'POS ID Format',
                                    default=_default_pos_id_format,
                                    track_visibility=True)
    new_lease_term = fields.Many2one('pms.leaseterms',
                                     string="Add New Lease Term",
                                     default=_default_new_lease_term,
                                     track_visibility=True)
    extend_lease_term = fields.Many2one('pms.leaseterms',
                                        string="Extened Lease Term",
                                        default=_default_lease_extend_term,
                                        track_visibility=True)
    lease_agre_format_id = fields.Many2one(
        'pms.format',
        'Lease Agreement Format',
        default=_default_lease_agreement_format,
        track_visibility=True)
    rentschedule_type = fields.Selection(
        [('prorated', "Prorated"), ('calendar', "Calendar")],
        default='prorated',
        string="Rent Schedule Type",
        track_visibility=True,
    )
    extend_count = fields.Integer("Extend count",
                                  track_visibility=True,
                                  default=3)
    pre_notice_terminate_term = fields.Integer("Pre-Terminate Term(Days)",
                                               default=30,
                                               track_visibility=True)
    prospect_format_id = fields.Many2one(
        'pms.format',
        'Prospect Format',
        readonly=False)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_multi_property = fields.Boolean("Manage multiple properties", implied_group='property_management_system.group_multi_property')
    current_property_id = fields.Many2one('pms.properties', string='Properties', required=True,
        default=lambda self: self.env.user.current_property_id)
    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)
    property_code_len = fields.Integer("Property Code Length",
                                       related="company_id.property_code_len",
                                       readonly=False)
    floor_code_len = fields.Integer('Floor Code Length',
                                    related='company_id.floor_code_len',
                                    readonly=False)
    # space_unit_code_len = fields.Integer(
    #     'Space Unit Code Length',
    #     related="company_id.space_unit_code_len",
    #     readonly=False)
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
    lease_agre_format_id = fields.Many2one(
        'pms.format',
        'Lease Format',
        related="company_id.lease_agre_format_id",
        readonly=False)
    rentschedule_type = fields.Selection(
        [('prorated', "Prorated"), ('calendar', "Calendar")],
        string="Rent Schedule",
        related="company_id.rentschedule_type",
        readonly=False)
    extend_count = fields.Integer("Extend count",
                                  related="company_id.extend_count",
                                  readonly=False)
    pre_notice_terminate_term = fields.Integer(
        "Pre-Terminate Term(Days)",
        related="company_id.pre_notice_terminate_term",
        readonly=False)
    prospect_format_id = fields.Many2one(
        'pms.format',
        'Prospect Format',
        related="company_id.prospect_format_id",
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

    @api.onchange('prospect_format_id')
    def onchange_prospect_format_id(self):
        if self.prospect_format_id:
            self.company_id.prospect_format_id = self.prospect_format_id

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

    # @api.onchange('space_unit_code_len')
    # def onchange_space_unit_code_len(self):
    #     if self.space_unit_code_len:
    #         self.company_id.space_unit_code_len = self.space_unit_code_len

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

    name = fields.Char("Description", required=True, track_visibility=True)
    term_type = fields.Selection([('newlt',"New Leaseterm"),('extlt',"Extend Leaseterm")])
    sample = fields.Char("Sample",compute="_compute_sample_format", store=True)
    lease_period_type = fields.Selection([('month', "Month"),
                                          ('year', "Year")],
                                         string="Lease Period Type",
                                         track_visibility=True)
    min_time_period = fields.Integer("Min Time Period", track_visibility=True)
    max_time_period = fields.Integer("Max Time Period", track_visibility=True)
    notify_period = fields.Integer("Notice Period(Month)",
                                   track_visibility=True)
    active = fields.Boolean("Active", default=True, track_visibility=True)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            sample = record.sample
            result.append((record.id, sample))
        return result
    
    @api.model
    def create(self, values):
        format_id = self.search([('name', '=', values['name'])])
        if format_id:
            raise UserError(_("%s is already existed." % values['name']))
        return super(PMSLeaseTerms, self).create(values)

    @api.multi
    def write(self, vals):
        format_id = None
        if 'name' in vals:
            sample_id = self.search([('name', '=', vals['name'])])
            if sample_id:
                raise UserError(_("%s is already existed." % vals['name']))
        return super(PMSLeaseTerms, self).write(vals)
    

    @api.depends('term_type','lease_period_type','min_time_period','max_time_period','notify_period')
    def _compute_sample_format(self):
        format = ""
        if self.term_type =="newlt":
            format = "NLT"
        if self.term_type =="extlt":
            format = "ELT"
        if self.lease_period_type == "month":
            format += " Month("
            if self.notify_period:
                format += "N-"
                format += str(self.notify_period)
                format += "|"
            if self.min_time_period:
                format += "Min-"
                format += str(self.min_time_period)
                format += "|"
            if self.max_time_period:
                format += "Max-"
                format += str(self.max_time_period)
            format += ")"
        if self.lease_period_type == "year":
            format += " Year("
            if self.notify_period:
                format += "N-"
                format += str(self.notify_period)
                format += "|"
            if self.min_time_period:
                format += "Min-"
                format += str(self.min_time_period)
                format += "|"
            if self.max_time_period:
                format += "Max-"
                format += str(self.max_time_period)
            format += ")"
        self.sample = format
        
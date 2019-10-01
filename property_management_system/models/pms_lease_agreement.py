from odoo import models, fields, api, tools


class PMSLeaseAgreement(models.Model):
    _name = 'pms.lease_agreement'
    _description = "Lease Agreements"

    name = fields.Char("Shop Name",
                       default="New",
                       related="company_tanent_id.name")
    property_id = fields.Many2one("pms.properties")
    company_tanent_id = fields.Many2one("res.company", "Shop")
    # tenant_type = fields.Char(related="company_tanent_id.company_type.name")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    extend_to = fields.Date("Extend Date")
    old_end_date = fields.Date("OLED")
    vendor_type = fields.Char("Vendor Type")
    company_vendor_id = fields.Many2one('res.company', "Vendor")
    currency_id = fields.Many2one('res.currency', "Currency")
    pos_submission = fields.Boolean("Pos Submission")
    pos_submission_type = fields.Selection([('fpt', 'FTP'), ('ws', 'WS SOAP'),
                                            ('rap', 'Restful API'),
                                            ('manual', 'Manual')],
                                           "Submission Type",
                                           default='fpt')
    sale_data_type = fields.Selection([('TRAN', 'Transaction'),
                                       ('TRANW', 'Transaction /w Item'),
                                       ('DAILYSALE', 'Daily Sales'),
                                       ('MONTHLYSALE', 'Monthly Sales')],
                                      "Sales Data Type",
                                      default='TRAN')
    pos_submission_frequency = fields.Selection([('15MINUTE', '15 Minutes'),
                                                 ('DAILY', 'Daily'),
                                                 ('MONTHLY', 'Monthly')],
                                                "Submit Frequency",
                                                default='15MINUTE')
    reset_gp_flat = fields.Boolean("Reset GP Flag")
    reset_date = fields.Date("Reset Date")
    remark = fields.Text("Remark")
    state = fields.Selection([('NEW', "New"), ('RENEWED', 'Renewed'),
                              ('TERMINATED', 'Terminated'),
                              ('EXTENDED', "Extended"),
                              ('CANCELLED', "Cancelled"),
                              ('EXPIRED', "Expired")],
                             string="Status",
                             default="NEW")
    active = fields.Boolean(default=True)
    lease_agreement_line = fields.One2many("pms.lease_agreement.line",
                                           "lease_agreement_id",
                                           "Lease Agreement Items")
    rental_charge_type = fields.Selection([('base', 'Base'),
                                           ('base+gto', 'Base + GTO'),
                                           ('baseorgto', 'Base or GTO')],
                                          string="Rental Charge Type")

    @api.multi
    def toggle_active(self):
        for la in self:
            if not la.active:
                la.active = self.active
        super(PMSLeaseAgreement, self).toggle_active()

    # _sql_constraints = [
    #     ('name_unique', 'unique(name)',
    #      'Please add other name that is exiting in the database.')
    # ]


class PMSLeaseAgreementLine(models.Model):
    _name = 'pms.lease_agreement.line'
    _description = "Lease Agreement Line"

    lease_agreement_id = fields.Many2one("pms.lease_agreement",
                                         "Lease Agreement")

    unit_no = fields.Many2one("pms.space.unit")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    extend_to = fields.Date("Extend Date")
    company_tanent_id = fields.Many2one(
        'res.company',
        "Shop",
    )
    pos_id = fields.Char("POS ID")
    remark = fields.Text("Remark")


class PMSChargeType(models.Model):
    _name = 'pms.charge_type'
    _description = "Charge Types"

    name = fields.Char("Description", required=True)
    code = fields.Char("Code", required=True)
    active = fields.Boolean(default=True)
    _sql_constraints = [
        ('name_code_unique', 'unique(code)',
         'Please add other CODE that is exiting in the database.')
    ]

    @api.multi
    def toggle_active(self):
        for la in self:
            if not la.active:
                la.active = self.active
        super(PMSChargeType, self).toggle_active()


class PMSChargeFormula(models.Model):
    _name = 'pms.charge.formula'
    _description = "Charge Formulas"

    name = fields.Char("Description", required=True)
    code = fields.Char("Code", required=True)
    active = fields.Boolean(default=True)
    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'Please add other CODE that is exiting in the database.')
    ]

    @api.multi
    def toggle_active(self):
        for la in self:
            if not la.active:
                la.active = self.active
        super(PMSChargeFormula, self).toggle_active()


class PMSTradeCategory(models.Model):
    _name = "pms.trade_category"
    _description = "Trade Category"

    name = fields.Char("Descritpion", required=True)
    code = fields.Char("Code", required=True)
    active = fields.Boolean(default=True)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.name
            result.append((record.id, code))
        return result


class PMSSubTradeCategory(models.Model):
    _name = "pms.sub_trade_category"
    _description = "Sub Trade Category"

    name = fields.Char("Description", required=True)
    code = fields.Char("Code", required=True)
    trade_id = fields.Many2one("pms.trade_category", "Trade")
    active = fields.Boolean(default=True)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.name
            result.append((record.id, code))
        return result
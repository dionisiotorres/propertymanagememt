# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PMSLeaseUnitPos(models.Model):
    _name = "pms.lease.unit.pos"
    _description = "Lease Unit POS"

    name = fields.Char("Name", readonly=1)
    appaccesskey = fields.Char("AppAccessKey")
    appsecretaccesskey = fields.Char("AppSecretAccessKey")
    leaseagreementitem_id = fields.Many2one("pms.lease_agreement.line",
                                            "LeaseAgreementItemID")
    posinterfacecode_id = fields.Many2one("pms.lease.interface.code",
                                          "PosInterfaceCode",
                                          required=True)
    spaceunit_id = fields.Char("SpaceUnitID")
    useposid = fields.Boolean("UsePosID")
    inactivedate = fields.Date("InactiveDate")
    active = fields.Boolean("Active", default=True)

    @api.onchange('posinterfacecode_id')
    def onchange_posinterfacecode_id(self):
        domain = {}
        if self.leaseagreementitem_id and not self.posinterfacecode_id:
            leaseunit_ids = self.leaseagreementitem_id
            if leaseunit_ids.property_id:
                property_id = leaseunit_ids.property_id
                if property_id.is_autogenerate_posid == True:
                    for prop in property_id:
                        if not prop.pos_id_format:
                            raise UserError(
                                _("Please set POSID Format in this property setting."
                                  ))
                        if prop.pos_id_format and prop.pos_id_format.format_line_id:
                            val = []
                            for ft in prop.pos_id_format.format_line_id:
                                if ft.value_type == 'dynamic':
                                    if property_id.code and ft.dynamic_value == 'property code':
                                        val.append(property_id.code)
                                if ft.value_type == 'fix':
                                    val.append(ft.fix_value)
                                if ft.value_type == 'digit':
                                    sequent_ids = self.env[
                                        'ir.sequence'].search([
                                            ('name', '=', 'Lease Agreement')
                                        ])
                                    sequent_ids.write(
                                        {'padding': ft.digit_value})
                                if ft.value_type == 'datetime':
                                    mon = yrs = ''
                                    if ft.datetime_value == 'MM':
                                        mon = datetime.today().month
                                        val.append(mon)
                                    if ft.datetime_value == 'MMM':
                                        mon = datetime.today().strftime('%b')
                                        val.append(mon)
                                    if ft.datetime_value == 'YY':
                                        yrs = datetime.today().strftime("%y")
                                        val.append(yrs)
                                    if ft.datetime_value == 'YYYY':
                                        yrs = datetime.today().strftime("%Y")
                                        val.append(yrs)
                            space = []
                            leasepos_no_pre = ''
                            if len(val) > 0:
                                for l in range(len(val)):
                                    leasepos_no_pre += str(val[l])
                    leasepos_no = ''
                    company_id = self.env.user.company_id.id
                    leasepos_no += self.env['ir.sequence'].with_context(
                        force_company=company_id).next_by_code(
                            'pms.lease.interface.code')
                    posinterface_id = self.posinterfacecode_id.create(
                        {'name': leasepos_no_pre + leasepos_no})
                    self.posinterfacecode_id = posinterface_id
                    # if not self.posinterfacecode_id:
                    #     leaseunit_ids = self.leaseagreementitem_id
                    #     if leaseunit_ids.property_id:
                    #         property_id = leaseunit_ids.property_id
                    #         if property_id.is_autogenerate_posid != True:
                    interfacecode = self.env[
                        'pms.lease.interface.code'].search([])
                    intids = []
                    psids = []
                    data = []
                    for intid in interfacecode:
                        intids.append(intid.id)
                    psids = self.leaseagreementitem_id.get_interfacecode(
                        intids)
                    for pids in interfacecode:
                        if pids.id not in psids[0]:
                            data.append(pids.id)
                    domain = {'posinterfacecode_id': [('id', 'in', data)]}
                    return {'domain': domain}
        if self.leaseagreementitem_id and not self.posinterfacecode_id:
            interfacecode = self.env['pms.lease.interface.code'].search([])
            intids = []
            psids = []
            data = []
            for intid in interfacecode:
                intids.append(intid.id)
            psids = self.leaseagreementitem_id.get_interfacecode(intids)
            for pids in interfacecode:
                if pids.id not in psids[0]:
                    data.append(pids.id)
            domain = {'posinterfacecode_id': [('id', 'in', data)]}
            return {'domain': domain}


class PMSLeaseInterfaceCode(models.Model):
    _name = "pms.lease.interface.code"
    _description = "POS Code"

    name = fields.Char("Name")

    _sql_constraints = [('name_unique', 'unique(name)',
                         'Your name is exiting in the database.')]

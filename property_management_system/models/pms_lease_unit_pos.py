# -*- coding: utf-8 -*-
import json
import datetime
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError
from odoo.addons.property_management_system.models import api_rauth_config


class PMSLeaseUnitPos(models.Model):
    _name = "pms.lease.unit.pos"
    _description = "Lease Unit POS"
                
    name = fields.Char("Name", readonly=1)
    appaccesskey = fields.Char("AppAccessKey")
    appsecretaccesskey = fields.Char("AppSecretAccessKey")
    leaseagreement_id = fields.Many2one("pms.lease_agreement",
                                            "LeaseAgreement")
    leaseagreementitem_id = fields.Many2one("pms.lease_agreement.line",
                                            "LeaseAgreementItemID")
    posinterfacecode_id = fields.Many2one("pms.lease.interface.code",
                                          "PosInterfaceCode",
                                          required=True)
    spaceunit_id = fields.Char("SpaceUnitID")
    useposid = fields.Boolean("UsePosID", default=True)
    posidisactive = fields.Boolean("PosIdIsActive", default=True)
    inactivedate = fields.Date("InactiveDate")
    active = fields.Boolean("Active", default=True)
    is_api_post = fields.Boolean("Posted")

    @api.onchange('leaseagreementitem_id')
    def onchange_leaseagreementitem_id(self):
        line_id = []
        self.onchange_posinterfacecode_id()
        if self.leaseagreement_id.lease_agreement_line:
            for lagel in self.leaseagreement_id.lease_agreement_line:
                    line_id.append(lagel.id)
            domain ={'leaseagreementitem_id':[('id','in', line_id)]}
            return {'domain':domain}


    @api.onchange('posinterfacecode_id')
    def onchange_posinterfacecode_id(self):
        domain = {}
        if self.leaseagreementitem_id and not self.posinterfacecode_id:
            leaseunit_ids = self.leaseagreementitem_id
            self.leaseagreement_id = self.leaseagreementitem_id.lease_agreement_id
            if leaseunit_ids.property_id:
                property_id = leaseunit_ids.property_id
                formats = ''
                leasepos_no_pre = ''
                model = 'Lease POS ID'
                if property_id.is_autogenerate_posid == True:
                    for prop in property_id:
                        if not prop.pos_id_format:
                            raise UserError(
                                _("Please set POSID Format in this property setting."
                                  ))
                        if prop.pos_id_format and prop.pos_id_format.format_line_id:
                            leasepos_no_pre, formats = leaseunit_ids.lease_agreement_id.get_pos_pre_format(model, prop, leasepos_no_pre)
                        leasepos_no = ''
                        sequent_ids = self.env['ir.sequence'].search([('name', '=', 'Lease POS ID'),('property_id','=',property_id.id),('code','=',formats)])
                        if not sequent_ids:
                            sequent_ids = self.env['ir.sequence'].create({'name':'Lease POS ID','property_id':property_id.id,'code': formats})

                        leasepos_no += str(self.env['ir.sequence'].with_context(
                            force_company=self.env.user.company_id.id,force_property = property_id.id).next_by_code(formats))
                        posinterface_id = self.posinterfacecode_id.create(
                            {'name': leasepos_no_pre + leasepos_no})
                        self.posinterfacecode_id = posinterface_id
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

    def leaseunitpos_schedular(self):
        values = None
        property_id = None
        leaseposids = []
        property_ids = self.env['pms.properties'].search([
            ('api_integration', '=', True), ('api_integration_id', '!=', False)
        ])
        for pro in property_ids:
            leaseipos_ids = self.search([('is_api_post', '=', False),
                                         ('leaseagreementitem_id', '!=', None)])
            if leaseipos_ids:
                for lp in leaseipos_ids:
                    property_id = lp.leaseagreementitem_id.property_id
                    leaseposids.append(lp.id)
                leaseipos_api_id = self.search([('is_api_post', '=', False),
                                                ('id', 'in', leaseposids)])
                if leaseipos_api_id:
                    integ_obj = property_id.api_integration_id
                    integ_line_obj = integ_obj.api_integration_line
                    api_line_ids = integ_line_obj.search([('name', '=',
                                                           "Leaseunitpos")])
                    datas = api_rauth_config.APIData.get_data(
                        leaseipos_api_id, values, property_id, integ_obj,
                        api_line_ids)
                    if datas:
                        if datas.res:
                            response = json.loads(datas.res)
                            if 'responseStatus' in response:
                                if response['responseStatus']:
                                    if 'message' in response:
                                        if response['message'] == 'SUCCESS':
                                            for lup in leaseipos_api_id:
                                                lup.write(
                                                    {'is_api_post': True})


class PMSLeaseInterfaceCode(models.Model):
    _name = "pms.lease.interface.code"
    _description = "POS Code"

    name = fields.Char("Name")

    _sql_constraints = [('name_unique', 'unique(name)',
                         'Your name is exiting in the database.')]

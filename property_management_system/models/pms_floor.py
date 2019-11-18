import base64
import json
import requests
import datetime as datetime
# from requests_oauth2 import OAuth2BearerToken
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from odoo.addons.property_management_system.models import api_rauth_config


class PMSFloor(models.Model):
    _name = 'pms.floor'
    _description = "PMS Floor"
    _order = "code,name"

    name = fields.Char("Description", required=True)
    code = fields.Char("Floor Code", required=True)
    floor_code_ref = fields.Char("Floor Ref Code")
    active = fields.Boolean("Active", default=True)
    property_id = fields.Many2one("pms.properties", "Property", required=True)

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

    @api.model
    def create(self, values):
        integ_obj = self.env['pms.api.integration']
        api_type = self.env['pms.api.type'].search([('name', '=', "Floor")])
        api_integ_id = integ_obj.search([('property_id', '=', values['property_id']), ('api_type', '=', api_type.name)])
        api_integ = []
        headers = {}
        payload = None
        if api_integ_id:
            api_integ = api_integ_id.generate_api_data({'id': api_integ_id.id, 'data': values})
            headers = api_integ['header']
            payload_code = str(values['code'])
            payload_name = str(values['name'])
            url_save = api_integ_id.url + api_integ_id.post_api
            modify_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            if values['active'] == True:
                payload_active = 'true'
            else:
                payload_active = 'false'
        id = None
        id = super(PMSFloor, self).create(values)
        if id:
            payload = str('{\r\n        \"floorID\": \"\",\r\n        \"floorCode\":') + '"' + str(payload_code) + '"' + str(',\r\n        \"floorDesc\":') + '"' + str(payload_name) + '"' + str(',\r\n        \"displayOrdinal\": null,\r\n       \"remark\": null,\r\n        \"ExtDataSourceID\":') + '"' + str("odoo") + '"' + str(',\r\n        \"ExtFloorID\":') + '"' + str(id) + '"' + str(',\r\n        \"ModifiedDate\":') + '"' + modify_date + '"' + str(',\r\n        \"active\":') + payload_active + str('\r\n    }')
            requests.request("POST", url_save, data=payload, headers=headers)
        return id

    @api.multi
    def write(self, vals):
        payload = f_id = payload_name = payload_code = payload_active = data = url = url_save = None
        headers = {}
        f_codes = []
        api_type = self.env['pms.api.type'].search([('name', '=', "Floor")])
        api_integ_id = self.env['pms.api.integration'].search([('property_id', '=', self.property_id.id), ('api_type', '=', api_type.name)])
        if api_integ_id:
            url = api_integ_id.url
            get_api = url + api_integ_id.get_api
            CLIENT_ID = api_integ_id.client_id
            CLIENT_SECRET = api_integ_id.client_secret
            access_token = api_integ_id.access_token
            authon = api_rauth_config.Auth2Client(url, CLIENT_ID, CLIENT_SECRET, access_token)
            url_save = api_integ_id.url  + api_integ_id.post_api
            with requests.Session() as s:
                s.auth = OAuth2BearerToken(authon.access_token)
                r = s.get(get_api)
                r.raise_for_status()
                data = r.json()
            for floor in data:
                f_codes.append(floor['floorCode'])
                if floor['floorCode'] == self.code and self.name == floor['floorDesc']:
                    f_id = floor['floorID']
            if 'name' in vals and authon.access_token:
                payload_name = str(vals['name'])        
            if 'code' in vals and authon.access_token:
                if vals['code'] in f_codes:
                    raise UserError(_("Floor Code %s is exiting in Database, Please set other Code." % (vals['code'])))
                else:
                    payload_code = str(vals['code'])
            if 'active' in vals and authon.access_token:
                if vals['active'] == True:
                    payload_active = 'true'
                else:
                    payload_active = 'false'
            if self.active == True:
                payload_active = 'true'
            else:
                payload_active = 'false'
            modify_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            payload = str('{\r\n        \"floorID\":"') + (f_id if f_id else "") + str('",\r\n        \"floorCode\":') + '"' + (payload_code if payload_code else self.code) + '"' + str(',\r\n        \"floorDesc\":') + '"' + (payload_name if payload_name else self.name) + '"' + str(',\r\n        \"displayOrdinal\": null,\r\n       \"remark\": null,\r\n        \"active\":') + payload_active + str('\r\n    }')
            host = url.split("//")[1]
            headers = {
                'Content-Type': "application/json",
                'Authorization': "Bearer " + authon.access_token,
                'User-Agent': "PostmanRuntime/7.15.2",
                'Accept': "*/*",
                'Cache-Control': "no-cache",
                'Host': host,
                'Accept-Encoding': "gzip, deflate",
                'Content-Length': "172",
                'Connection': "keep-alive",
                'cache-control': "no-cache"
            }
        return super(PMSFloor, self).write(vals), requests.request(
            "POST", url_save, data=payload, headers=headers)
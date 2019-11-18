import requests
import requests-oauth2
from odoo import api, fields, models
from requests-oauth2 import OAuth2BearerToken
from odoo.addons.property_management_system.models import api_rauth_config


class PMSApiIntegration(models.Model):
    _name = 'pms.api.integration'
    _description = "Api Integration"
    _orders = 'id, name'

    name = fields.Char("Name")
    url = fields.Char("URL")
    get_api = fields.Char("GET API")
    post_api = fields.Char('POST API')
    access_token = fields.Char("Access Token")
    client_id = fields.Char("Client ID")
    client_secret = fields.Char("Client Secret")
    api_type = fields.Many2one("pms.api.type", "API Type")
    property_id = fields.Many2one("pms.properties", "Property")
    active = fields.Boolean("Active", default=True)

    @api.multi
    def generate_api_data(self, values):
        payload = payload_name = payload_code = payload_active = url = url_save = None
        headers = {}
        CLIENT_ID = self.client_id
        CLIENT_SECRET = self.client_secret
        access_token = self.access_token
        url = self.url
        authon = api_rauth_config.Auth2Client(url, CLIENT_ID, CLIENT_SECRET,
                                              access_token)
        print(authon)
        get_api = url + self.get_api
        with requests.Session() as s:
            s.auth = OAuth2BearerToken(authon.access_token)
            r = s.get(get_api)
            r.raise_for_status()
            data = r.json()
        if authon.access_token:
            url_save = url + self.post_api
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
            return {'url': url_save, 'data': data, 'header': headers}


class PMSApiType(models.Model):
    _name = 'pms.api.type'
    _description = "API Type"
    _orders = 'id, name'

    name = fields.Char("Name")
import requests
import json
from odoo import tools, _
from rauth import OAuth2Service


class Auth2Client:
    def __init__(self, url, client_id, client_secret, access_token):
        self.access_token = self.service = self.url = None
        self.url = url
        self.service = OAuth2Service(
            name="foo",
            client_id=client_id,
            client_secret=client_secret,
            access_token_url=url + access_token,
            authorize_url=url + access_token,
            base_url=url,
        )
        return self.get_access_token()

    def get_access_token(self):
        data = {
            'code': 'bar',
            'grant_type': 'client_credentials',
            'redirect_uri': self.url
        }
        session = self.service.get_auth_session(data=data, decoder=json.loads)
        self.access_token = session.access_token

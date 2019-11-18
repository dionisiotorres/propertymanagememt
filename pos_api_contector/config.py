class ExampleOAuth2Client:
    def __init__(self, client_id, client_secret):
        self.access_token = None

        self.service = OAuth2Service(
            name="foo",
            client_id=client_id,
            client_secret=client_secret,
            access_token_url="http://zando.local:8072/connect/token",
            authorize_url="http://zando.local:8072/connect/token",
            base_url="http://zando.local:8072",
        )

        self.get_access_token()

    def get_access_token(self):
        data = {
            'code': 'bar',
            'grant_type': 'client_credentials',
            'redirect_uri': 'http://zando.local:8072'
        }

        session = self.service.get_auth_session(data=data, decoder=json.loads)

        self.access_token = session.access_token


# import urllib3
# import json
# import httplib
# import base64
# import urllib
# import json
# import requests
# import requests.auth

# def getAuthToken():
#     CLIENT_ID = "APIUSER"
#     CLIENT_SECRET = "5E817517-7D9D-430C-A0B3-905298EA741C"
#     TOKEN_URL = "http://zando.local:8072/connect/token/"

#     conn = httplib.HTTPSConnection("http://zando.local:8072")

#     url = "/connect/token/"

#     params = {"grant_type": "client_credentials"}

#     client = CLIENT_ID
#     client_secret = CLIENT_SECRET

#     authString = base64.encodestring(
#         '%s:%s' % (client, client_secret)).replace('\n', '')

#     requestUrl = url + "?" + urllib.urlencode(params)

#     headersMap = {
#         "Content-Type": "application/x-www-form-urlencoded",
#         "Authorization": "Basic " + authString
#     }

#     conn.request("POST", requestUrl, headers=headersMap)

#     response = conn.getresponse()

#     if response.status == 200:
#         data = response.read()
#         result = json.loads(data)

#         return result["access_token"]

# CLIENT_ID = "APIUSER"
# CLIENT_SECRET = "5E817517-7D9D-430C-A0B3-905298EA741C"
# TOKEN_URL = "http://zando.local:8072/connect/token/"

# # REDIRECT_URI = "https://www.getpostman.com/oauth2/callback"

# # base_url =
# # access_token_req = {
# #     "client_id": "APIUSER",
# #     "grant_type": "client_credentials",
# #     "client_secret": "5E817517-7D9D-430C-A0B3-905298EA741C",
# # }
# # http = urllib3.PoolManager()
# # URL = 'http://zando.local:8072'
# # root = '/api/floor/getFloors'  # the path where the request handler is located

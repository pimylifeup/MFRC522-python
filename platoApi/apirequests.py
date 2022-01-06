import requests
import json
from configuration import TokenIO
from configuration import ConfigurationIO

class ApiRequests:

    tokenIO = None
    configIO = None

    def __init__(self, configFilePath) -> None:
        self.configIO = ConfigurationIO(configFilePath)
        self.tokenIO = TokenIO(configFilePath)
        pass

    def RequestToken(self) -> str:

        # return url
        configJson = self.configIO.read_config()
        url = configJson["IdentityUrl"]
        user = configJson["User"]
        password = configJson["Password"]

        # query params
        body = {
            "grant_type": "password",
            "client_id": "reactSPA",
            "username": user,
            "password": password
        }

        headers = {
            'content-type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(
            url, 
            data=body, 
            headers=headers
            )

        responseText = response.text 
        print(responseText)
        tokenResponse = json.loads(responseText)

        accessToken = tokenResponse['access_token']
        self.tokenIO.write_token(accessToken)

        return accessToken


    # return the json response 
    def AuthorizeProfile(self, card_id, profile_id):
        appConfig = self.configIO.read_config
        url = appConfig['ProfileAuthUrl']

        # request token
        token:str = self.tokenIO.read_token()

        headers = {
            'content-type' : 'application/json',
            'Authorization': 'Bearer '+token
        }
        body = {
            "ProfileId": profile_id,
            "CardId":card_id
        }

        response = requests.post(url, headers=headers, data=json.dumps(body))

        if response.status_code != 200:
            return None

        return response.json()

        

        




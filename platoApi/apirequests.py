import requests
import json
from configuration import TokenIO
from configuration import ConfigurationIO
from configuration import ActionEnum

class ApiRequests:

    tokenIO = None
    configIO = None
    actionEnum = None

    def __init__(self, configFilePath) -> None:
        self.configIO = ConfigurationIO(configFilePath)
        self.tokenIO = TokenIO(configFilePath)
        self.actionEnum = ActionEnum()
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
        """"
        Send authorize request to the server, and gets infos about the profile
        the function returns the JSON-Obj
        """

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

    def SendTimestamp(self, action, profileId, cardId, securityToken, timestamp):
        """"
        Send the timestamp to the server and get a SuccessResponse
        the function returns the JSON-Obj
        """

        appConfig = self.configIO.read_config
        url = appConfig['TimeStampUrl']

        # request token
        token:str = self.tokenIO.read_token()

        headers = {
            'content-type' : 'application/json',
            'Authorization': 'Bearer '+token
        }

        actionValue = self.actionEnum.ReturnValue(action)
        body = {
            "Action":actionValue,
            "ProfileId":profileId,
            "CardId":cardId,
            "TokenTimeStamp":securityToken,
            "TimeStamp":timestamp
        }

        response = requests.post(url, headers=headers, data=json.dumps(body))

        if response.status_code != 200:
            return None

        return response.json()
        

        

        




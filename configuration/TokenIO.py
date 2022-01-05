import json
import os

class TokenIO:

    FILE_TOKEN = 'token.json'
    FULL_PATH = ''

    def __init__(self, base_path) -> None:
        self.FULL_PATH = os.path.join(base_path, self.FILE_TOKEN)
        print(self.FULL_PATH)
        pass

    def read_token(self) -> str:
        data = None

        try:
            with open(self.FULL_PATH, "r") as read_file:
                data = json.load(read_file)

        except:
            data = None

        if data == None:
            return None
        else:
            return data['token']

    
    def write_token(self, token:str) -> int:
        obj = {
            "token": token
        }

        try:
            with open(self.FULL_PATH, "w") as write_file:
                json.dump(obj, write_file)

        except:
            return 0

        return 1
import logging
import datetime

class DebugHelper:

    verbose = False

    def __init__(self, verbose) -> None:
        logging.basicConfig(filename='app.log', filemode='a', encoding='utf-8', level=logging.DEBUG)
        self.verbose = verbose

    # helper functions
    def log(self, msg):
        d = datetime.datetime.now().strftime("%I:%M:%S")
        o = self.addingTimestampToMsg(msg)
        
        if self.verbose:
            print(o)
        
        logging.debug(o)


    def log_UID(self, list):
        content = ''
        for a in list:
            content += hex(a)+"-"

        content = content.rstrip("-")
        
        o = self.addingTimestampToMsg("UID "+content)
        
        if self.verbose:
            print(o)
        
        logging.debug(o)


    def addingTimestampToMsg(self, msg):
        d = datetime.datetime.now().strftime("%I:%M:%S")
        return (d+" : "+msg)
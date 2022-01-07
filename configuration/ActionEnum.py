# CheckIn
# CheckOut


class ActionEnum:

    ActionSelected = 0
    ButtonSelected = 0

    CHECK_IN = "CheckIn"
    CHECK_OUT = "CheckOut"

    def ActionSet(self, v):
        self.ActionSelected = v

    def ActionSetCheckIn(self):
        self.ActionSelected = 1

    def ActionSetCheckOut(self):
        self.ActionSelected = 2

    def ActionGet(self):
        return self.ActionSelected

    def ActionReset(self):
        self.ActionSelected = 0

    def ButtonSelectedYes(self):
        self.ButtonSelected = 1

    def ButtonSelectReset(self):
        self.ButtonSelected = 0

    def ClickCheckIn(self):
        self.ActionSetCheckIn()
        self.ButtonSelectedYes()
    
    def ClickCheckOut(self):
        self.ActionSetCheckOut()
        self.ButtonSelectedYes()

    def Reset(self):
        self.ActionReset()
        self.ButtonSelectReset()

    def TranslateValue(self, v) -> str:
        """
        Returns the value for TimeStampEnum Action
        1 = CheckIn
        2 = CheckOut
        """
        if v == 1:
            return self.CHECK_IN

        if v == 2:
            return self.CHECK_OUT

        return ""

    def GetActionName(self):
        """
        return the action as name from the class
        """
        return self.TranslateValue(self.ActionSelected)

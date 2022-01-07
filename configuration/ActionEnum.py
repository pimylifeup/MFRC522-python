
# CheckIn
# CheckOut


class ActionEnum:

    CHECK_IN = 'CheckIn'
    CHECK_OUT = 'CheckOut'

    def ReturnValue(self, v) -> str:
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

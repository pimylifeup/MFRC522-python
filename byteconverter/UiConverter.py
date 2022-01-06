


class UiConverter:

    def __init__(self) -> None:
        pass

    def to_UI_string(self, data:list) -> str:
        output = ''

        for i in data:
            if type(i) is int:
                hex_value = hex(i)
                hex_value = hex_value.replace('0x', '')
                if len(hex_value) == 1:
                    hex_value = '0'+hex_value

                output += (hex_value.upper() + '-')

        return output.strip('-')
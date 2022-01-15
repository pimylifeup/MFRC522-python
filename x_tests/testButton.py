
from gpiozero import Button

btn_in = Button(17)
btn_out = Button(18)

def btnA():
    print("A")

def btnB():
    print("B")

try:
    while True:
        btn_in.when_activated = btnA
        btn_out.when_activated = btnB

except KeyboardInterrupt:
    exit(1)
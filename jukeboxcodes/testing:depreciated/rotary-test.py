# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

from gpiozero import Button
from gpiozero import RotaryEncoder
from signal import pause

def printsteps(button):
    print(button.steps)

def action():
    print("pressed")

buttonpress = Button(26,bounce_time = 0.1) # just the pressed button

rotor = RotaryEncoder(19,13)
buttonpress.when_pressed = action
#rotor.when_rotated = printsteps
rotor.when_rotated_clockwise = printsteps

pause()

#yay!
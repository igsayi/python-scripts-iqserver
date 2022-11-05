#!/usr/bin/env python
import time

import pyautogui

pyautogui.FAILSAFE = False

while True:
    time.sleep(500)
    pyautogui.moveTo(100, 0)
    for i in range(0, 100):
        currentMouseX, currentMouseY = pyautogui.position()
        if currentMouseX != 100:
            continue
        pyautogui.moveTo(100, i * 5)
    for i in range(0, 3):
        pyautogui.press("shift")

#!/usr/bin/env python
import time

import pyautogui

pyautogui.FAILSAFE = False
prevMouseX, prevMouseY = pyautogui.position()
# print(time.localtime().tm_sec, "First position: ", pyautogui.position())
while True:
    time.sleep(50)
    currentMouseX, currentMouseY = pyautogui.position()
    # print("Curr vs Prev", currentMouseX, prevMouseX)
    if currentMouseX == prevMouseX:
        pyautogui.moveTo(100, 0)
    for i in range(0, 500):
        currentMouseX, currentMouseY = pyautogui.position()
        if currentMouseX != 100:
            prevMouseX, prevMouseY = pyautogui.position()
            # print(time.localtime().tm_sec, "position 1: ", i, pyautogui.position())
            break
        pyautogui.moveTo(100, i * 2)
        # print(time.localtime().tm_sec, "position 2: ", i, pyautogui.position())
        prevMouseX, prevMouseY = pyautogui.position()
    for i in range(0, 3):
        pyautogui.press("shift")

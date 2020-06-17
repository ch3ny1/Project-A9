#!/usr/bin/env python3
import asyncio

from aioconsole import ainput

from joycontrol import logging_default as log, utils
from joycontrol.controller import Controller
from joycontrol.controller_state import ControllerState, button_push
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server

import cv2 as cv

indicator_entering = cv.imread('indicator.ppm')
checker_exit = cv.imread('checker.ppm')
time2run = False

cap = cv.VideoCapture(0)
if not cap.isOpened():
        print("Cannot open camera")
        exit()

async def farm(controller_state: ControllerState):
    await button_push(controller_state, 'zr', sec=0.1)
    await asyncio.sleep(0.2)
    await button_push(controller_state, 'a', sec=0.1)
    await asyncio.sleep(0.4)
    await button_push(controller_state, 'down')
    await asyncio.sleep(0.1)
    await button_push(controller_state, 'left')
    await asyncio.sleep(0.034)
    await button_push(controller_state, 'right')

async def is_loading():
    global time2run
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame")
            break
        indicator = frame[575:595,960:990,0:3]
        if not cv.absdiff(indicator_entering,indicator).any():
            checker = frame[750:770, 1310:1340,0:3]
            if cv.absdiff(checker_exit,checker).any():
                time2run = True
        if cv.waitKey(1) == ord('q'):
            break

async def running(controller_state: ControllerState):
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'plus')
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'down', sec=2)
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'a')
    await asyncio.sleep(4)


async def farmInt(controller_state: ControllerState):
    global time2run
    user_input = asyncio.ensure_future(
        ainput(prompt='Farming initiated... Press <enter> to stop.')
    )
    asyncio.ensure_future(is_loading())
    
    while not user_input.done():
        if user_input.done():
                break
        
        while not time2run:
            await farm(controller_state)
    
        await running(controller_state)
        time2run = False
    
    cap.release()
    await user_input

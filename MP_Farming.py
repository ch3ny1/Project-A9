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
loading = False

cap = cv.VideoCapture(0)
if not cap.isOpened():
        print("Cannot open camera")
        exit()

frame = cap.read()

async def capturing():
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")




async def farm(controller_state: ControllerState):
    await button_push(controller_state, 'zr', sec=0.1)
    await asyncio.sleep(0.2)
    await button_push(controller_state, 'a', sec=0.1)
    await asyncio.sleep(0.4)
    await button_push(controller_state, 'down', sec=0.1)
    await asyncio.sleep(0.1)
    await button_push(controller_state, 'left', sec=0.034)
    await asyncio.sleep(0.034)
    await button_push(controller_state, 'right', sec=0.034)

async def is_loading():
    ret, frame = cap.read()
    indicator = frame[575:595,960:990,0:3]
    diff = cv.absdiff(indicator_entering,indicator)
    loading = diff.any()

async def betterRun():
    ret, frame = cap.read()

    while loading:
        checker = frame[750:770, 1310:1340,0:3]
        diff = cv.absdiff(checker_exit,checker)
        if diff.any():
            return True
        await is_loading()

    return False

async def running(controller_state: ControllerState):
    await asyncio.sleep(1)
    await button_push(controller_state, 'plus')
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'down', sec=2)
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'a')
    await asyncio.sleep(4)
    loading = False


async def farmInt(controller_state: ControllerState):
    user_input = asyncio.ensure_future(
        ainput(prompt='Pressing all buttons... Press <enter> to stop.')
    )
    while not user_input.done():
        if user_input.done():
                break

        await is_loading()
        while not loading:
            farm(controller_state)
            await is_loading()

        if await betterRun():
                await running(controller_state)


    await user_input

async def test_controller_buttons(controller_state: ControllerState):
    """
    Example controller script.
    Navigates to the "Test Controller Buttons" menu and presses all buttons.
    """


    # Goto settings
    await button_push(controller_state, 'down', sec=1)
    await button_push(controller_state, 'right', sec=2)
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'left')
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.3)

    # go all the way down
    await button_push(controller_state, 'down', sec=4)
    await asyncio.sleep(0.3)

    # goto "Controllers and Sensors" menu
    for _ in range(2):
        await button_push(controller_state, 'up')
        await asyncio.sleep(0.3)
    await button_push(controller_state, 'right')
    await asyncio.sleep(0.3)

    # go all the way down
    await button_push(controller_state, 'down', sec=3)
    await asyncio.sleep(0.3)

    # goto "Test Input Devices" menu
    await button_push(controller_state, 'up')
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.3)

    # goto "Test Controller Buttons" menu
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.3)

    # push all buttons except home and capture
    button_list = controller_state.button_state.get_available_buttons()
    if 'capture' in button_list:
        button_list.remove('capture')
    if 'home' in button_list:
        button_list.remove('home')

    user_input = asyncio.ensure_future(
        ainput(prompt='Pressing all buttons... Press <enter> to stop.')
    )

    # push all buttons consecutively until user input
    while not user_input.done():
        for button in button_list:
            await button_push(controller_state, button)
            await asyncio.sleep(0.1)

            if user_input.done():
                break

    # await future to trigger exceptions in case something went wrong
    await user_input

    # go back to home
    await button_push(controller_state, 'home')
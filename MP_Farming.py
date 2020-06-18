#!/usr/bin/env python3
import asyncio

from aioconsole import ainput

from joycontrol import logging_default as log, utils
from joycontrol.controller import Controller
from joycontrol.controller_state import ControllerState, button_push
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server

import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
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
    await button_push(controller_state, 'left', sec=0.034)
    await asyncio.sleep(0.034)
    await button_push(controller_state, 'right', sec=0.034)
    await asyncio.sleep(1)

def is_loading():
    global time2run
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame")
    indicator = frame[575:595,960:990,0:3]
    cv.imshow('indicator', indicator)
    diff = False
    while not cv.absdiff(indicator_entering,indicator).any():
        checker = frame[750:770, 1310:1340,0:3]
        cv.imshow('checker',checker)
        diff = cv.absdiff(checker_exit,checker).any()
        
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame")
            break
        indicator = frame[575:595,960:990,0:3]
        cv.imshow('indicator', indicator)
    time2run = diff

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
    print('Farming started.')
    farming = True

    user_input = asyncio.ensure_future(
        ainput(prompt='Pressing all buttons... Press <enter> to stop.')
    )

    # push all buttons consecutively until user input
    while not user_input.done():
        is_loading()
        while not time2run:
            is_loading()
            await farm(controller_state)
            if user_input.done():
                farming = False
                break
        
        print('Start running')
        await running(controller_state)
        time2run = False
        print('Run away')
        
        if not farming:
            break

            
    await user_input
    cap.release()

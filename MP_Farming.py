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
checker_gray = cv.cvtColor(checker_exit, cv.COLOR_BGR2GRAY)
time2run = False
count_played = 0
count_quitted = 0

cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

async def farm(controller_state: ControllerState):
    #await button_push(controller_state, 'zr', sec=0.1)
    #await asyncio.sleep(0.2)
    await button_push(controller_state, 'a', sec=0.1)
    await asyncio.sleep(0.1)
    await button_push(controller_state, 'y', sec=0.1)
    await asyncio.sleep(0.1)
    #await asyncio.sleep(0.4)
    #await button_push(controller_state, 'down')
    #await asyncio.sleep(0.1)
    #await button_push(controller_state, 'left', sec=0.034)
    #await asyncio.sleep(0.034)
    #await button_push(controller_state, 'right', sec=0.034)
    #await asyncio.sleep(1)


async def is_loading():
    global time2run
    global count_played

    waiting2quit = False
    loaded = False
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Can't receive frame")

        indicator = frame[575:595,960:990,0:3]
        cv.imshow('indicator', indicator)
        checker = frame[750:770, 1310:1340,0:3]
        cv.imshow('checker',checker)

        loading = not cv.absdiff(indicator_entering,indicator).any()

        if loading:
            loaded = True
            if waiting2quit:
                continue
            elif cv.absdiff(checker_gray,cv.cvtColor(checker, cv.COLOR_BGR2GRAY)).any():
                waiting2quit = True
                print('Too many players. Better run.')
                continue
        elif waiting2quit:
            time2run = True
            break
        elif loaded:
            count_played += 1
            break
        else:
            break

async def running(controller_state: ControllerState):
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'plus',sec=0.1)
    await asyncio.sleep(1.5)
    await button_push(controller_state, 'down', sec=2.5)
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'a',sec=0.1)
    await asyncio.sleep(4)


async def farmInt(controller_state: ControllerState):
    global time2run
    global cap
    global count_quitted
    global count_played
    print('Farming started.')
    farming = True

    user_input = asyncio.ensure_future(
        ainput(prompt='Farming in process... Press any key to stop.')
    )

    while not user_input.done():
        

        while not time2run:
            await farm(controller_state)
            await is_loading()
            if user_input.done():
                farming = False
                break
            
        if not farming:
            break

        if time2run:
            print('Escaping')
            await running(controller_state)
            time2run = False
            print('Run away and starting again')
            count_quitted += 1


        
    print('Played: ' + str(count_played))
    print('Quitted: ' + str(count_quitted))

    cap.release()
    cv.destroyAllWindows()
    await user_input
    
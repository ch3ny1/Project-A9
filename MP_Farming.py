#!/usr/bin/env python3
import asyncio
import numpy as np
import cv2 as cv

from aioconsole import ainput

from joycontrol import logging_default as log, utils
from joycontrol.controller import Controller
from joycontrol.controller_state import ControllerState, button_push
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server


from matplotlib import pyplot as plt
#indicator_entering = cv.imread('indicator.ppm')
#checker_exit = cv.imread('checker.ppm')
redflag = cv.imread('redFlag.ppm')
bckgrd = cv.imread('non.ppm')
missed_frame = cv.imread('missed.ppm')

#time2run = False
count_played = 0
count_quitted = 0

cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

async def farm(controller_state: ControllerState):
    await button_push(controller_state, 'zr', sec=0.1)
    await asyncio.sleep(0.1)
    await button_push(controller_state, 'a', sec=0.1)
    await asyncio.sleep(0.1)
    #await button_push(controller_state, 'zr', sec=0.1)
    await asyncio.sleep(0.4)
    #await button_push(controller_state, 'right', sec=0.034)
    #await asyncio.sleep(0.034)
    #await asyncio.sleep(0.4)
    await button_push(controller_state, 'down', sec=0.034)
    await asyncio.sleep(0.034)
    await button_push(controller_state, 'left')
    #await asyncio.sleep(0.034)
    await button_push(controller_state, 'right')
    await asyncio.sleep(0.2)




async def running(controller_state: ControllerState):
    await asyncio.sleep(0.4)
    await button_push(controller_state, 'plus',sec=0.1)
    await asyncio.sleep(1)
    await button_push(controller_state, 'down', sec=1.3)
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'a',sec=0.1)
    await asyncio.sleep(5)
    await button_push(controller_state, 'a', sec = 0.1)
    await asyncio.sleep(1.5)
    await button_push(controller_state, 'a', sec = 0.1)

"""
async def time2run(loaded=False, waiting2quit=False):
    global count_played
    global count_quitted

    ret, frame = cap.read()

    if (not ret) or (not cv.absdiff(frame,missed_frame).any()):
        print("Skipped a frame")
        return await time2run(loaded, waiting2quit)
    else:

        Pos_1 = frame[220:228, 280:288, 0:3]
        Pos_2 = frame[730:736, 992:998, 0:3]

        loading = not cv.absdiff(Pos_1, redflag).any()

        if loading:

            if loaded:
                if time2run:
                #print('Cant wait to run!')
                #await asyncio.sleep(1)
                    return await time2run(True, True)
                else:
                    #return await time2run(True, False)
                    return False
            elif cv.absdiff(Pos_2, bckgrd).any():
                print('\Too many people. Better run.')
                #await asyncio.sleep(1)
                return await time2run(True, True)
            else:
                print('Nice round!')
                #count_played+=1
                return False

        elif waiting2quit:
            count_quitted+=1
            return True
        else:
            return False

    return False
"""

def time2run(waiting2quit=False, loaded=False):
    global count_played
    global count_quitted


    while True:

        ret, frame = cap.read()
        if (not ret) or (not cv.absdiff(frame,missed_frame).any()):
            print("Skipped a frame")
            continue

        Pos_1 = frame[220:228, 280:288, 0:3]
        Pos_2 = frame[730:736, 992:998, 0:3]

        loading = not cv.absdiff(Pos_1, redflag).any()

        if loading:
            if waiting2quit:
                continue

            elif cv.absdiff(Pos_2, bckgrd).any():
                waiting2quit = True
                print('Too many people. Prepare for withdrawl.')
                count_quitted += 1
                continue
            else:
                loaded = True
                continue
        else:
            break

    if waiting2quit:
        #waiting2quit = False
        return True
    elif loaded:
        print('Nice round. Prepare for 9500 credits!')
        count_played += 1
        return False
    else:
        return False



async def farmInt(controller_state: ControllerState):
    #global time2run
    global cap
    global count_quitted
    global count_played
    print('Farming started.')
    farming = True

    user_input = asyncio.ensure_future(
        ainput(prompt='Farming in process... Press any key to stop.')
    )

    while not user_input.done():
        if not farming:
            cap.release()
            cv.destroyAllWindows()
            break

        #while not await time2run():
        elif not time2run(False, False):
            await farm(controller_state)

            if user_input.done():
                farming = False
                break

        else:
            print('Outta here')
            await running(controller_state)
            print('Run away and start again')



    print('Played: ' + str(count_played))
    print('Quitted: ' + str(count_quitted))

    #cap.release()
    #cv.destroyAllWindows()
    await user_input
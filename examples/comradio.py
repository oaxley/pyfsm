# -*- coding: utf-8 -*-
#
# This file is part of the pyfsm (AI Mechanics & Tech FSM) project
#
# Copyright 2019 AI Mechanics & Tech
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# this example simulates a simple COM radio like the Bendix/King KY196
# as found in basic planes.
#

# imports
#----------
import time
import queue
import pyfsm


# constants
#----------
AIRCOM_MINIMUM_FREQUENCY = 118.000
AIRCOM_MAXIMUM_FREQUENCY = 135.975
AIRCOM_CHANNEL_BANDWIDTH = 25.0 / 1000.0


# global vars
#----------
# active and standby frequencies
active = None
standby = None

# FSM objects
myFSM = None
states = list()
events = list()
transitions = list()


# functions
#----------
def user_callback(action):
    """ the callback used when state is changed """
    global active, standby

    # turn on the avionics
    if action == "on":
        # wait some time to simulate the avionics startup
        time.sleep(2)
        active = AIRCOM_MINIMUM_FREQUENCY
        standby = AIRCOM_MINIMUM_FREQUENCY

    # turn off the avionics
    if action == "off":
        active = None
        standby = None
        return False

    # swap active and standby frequency
    if action == "swap":
        active, standby = standby, active

    # do nothing for ready
    if action == "ready":
        return False

    # increase/decrease the integer part of the frequency
    if action == "+int":
        standby = standby + 1
    if action == "-int":
        standby = standby - 1

    # increase/decrease the decimal part of the frequency
    if action == "+dec":
        standby = standby + AIRCOM_CHANNEL_BANDWIDTH
    if action == "-dec":
        standby = standby - AIRCOM_CHANNEL_BANDWIDTH

    # boundary checks
    if standby < AIRCOM_MINIMUM_FREQUENCY:
        standby = AIRCOM_MAXIMUM_FREQUENCY
    elif standby > AIRCOM_MAXIMUM_FREQUENCY:
        standby = AIRCOM_MINIMUM_FREQUENCY

    # move back to "ready" state
    return True


# begin
#----------
# define events
events.append(pyfsm.Event("E.OFF"))
events.append(pyfsm.Event("E.ON"))
events.append(pyfsm.Event("E.READY"))
events.append(pyfsm.Event("E.SWAP"))

events.append(pyfsm.Event("E.+INT"))
events.append(pyfsm.Event("E.-INT"))
events.append(pyfsm.Event("E.+DEC"))
events.append(pyfsm.Event("E.-DEC"))

# define states
states.append(pyfsm.State("S.OFF", pyfsm.StateType.FSM_BEGIN_STATE, "off"))
states.append(pyfsm.State("S.ON", pyfsm.StateType.FSM_NORMAL_STATE, "on"))
states.append(pyfsm.State("S.READY", pyfsm.StateType.FSM_NORMAL_STATE, "ready"))
states.append(pyfsm.State("S.SWAP", pyfsm.StateType.FSM_NORMAL_STATE, "swap"))

states.append(pyfsm.State("S.+INT", pyfsm.StateType.FSM_NORMAL_STATE, "+int"))
states.append(pyfsm.State("S.-INT", pyfsm.StateType.FSM_NORMAL_STATE, "-int"))
states.append(pyfsm.State("S.+DEC", pyfsm.StateType.FSM_NORMAL_STATE, "+dec"))
states.append(pyfsm.State("S.-DEC", pyfsm.StateType.FSM_NORMAL_STATE, "-dec"))

# define transitions
transitions.append(pyfsm.Transition(events[1], states[0], states[1]))       # ON   : OFF -> ON
transitions.append(pyfsm.Transition(events[2], states[1], states[2]))       # READY: ON -> READY
transitions.append(pyfsm.Transition(events[0], states[2], states[0]))       # OFF  : READY -> OFF

transitions.append(pyfsm.Transition(events[3], states[2], states[3]))       # SWAP : READY -> SWAP
transitions.append(pyfsm.Transition(events[2], states[3], states[2]))       # READY: SWAP -> READY

transitions.append(pyfsm.Transition(events[4], states[2], states[4]))       # +INT : READY -> +INT
transitions.append(pyfsm.Transition(events[2], states[4], states[2]))       # READY: +INT -> READY
transitions.append(pyfsm.Transition(events[5], states[2], states[5]))       # -INT : READY -> -INT
transitions.append(pyfsm.Transition(events[2], states[5], states[2]))       # READY: -INT -> READY

transitions.append(pyfsm.Transition(events[6], states[2], states[6]))       # +DEC : READY -> +DEC
transitions.append(pyfsm.Transition(events[2], states[6], states[2]))       # READY: +DEC -> READY
transitions.append(pyfsm.Transition(events[7], states[2], states[7]))       # -DEC : READY -> -DEC
transitions.append(pyfsm.Transition(events[2], states[7], states[2]))       # READY: -DEC -> READY

# create the FSM
user_queue = queue.Queue()
myFSM = pyfsm.FSM()
myFSM.setup(user_callback, user_queue)
myFSM.add(transitions)
myFSM.start()

# main loop
avionics_is_on = False
while True:
    try:
        if active is None:
            print(f"active:[---.---] - standby:[---.---]")
        else:
            print(f"active:[{active:.003f}] - standby:[{standby:.003f}]")

        cmd = input(f"(qawsuo?)> ")

        # print help
        if cmd == '?':
            print("q: increase frequency by 1MHz")
            print("a: decrease frequency by 1MHz")
            print("w: increase frequency by 25kHz")
            print("s: decrease frequency by 25kHz")
            print("u: swap active/standby frequencies")
            print("o: avionics on/off")
            print("CTRL+C to quit")
            print("")

        # increase/decrease integer part
        if cmd == 'q':
            myFSM.update(events[4])
        if cmd == 'a':
            myFSM.update(events[5])

        # increase/decrease decimal part
        if cmd == 'w':
            myFSM.update(events[6])
        if cmd == 's':
            myFSM.update(events[7])

        # swap active/standby frequencies
        if cmd == 'u':
            myFSM.update(events[3])

        # turn on/off the avionics
        if cmd == 'o':
            if avionics_is_on:
                myFSM.update(events[0])
                avionics_is_on = False
            else:
                myFSM.update(events[1])
                avionics_is_on = True

        # execute callbacks
        while not user_queue.empty():
            callback = user_queue.get()

            if callback():
                myFSM.update(events[2])

            user_queue.task_done()

    except pyfsm.FSMError as error:
        print(f"!! {error}")

    except KeyboardInterrupt:
        break

print("")
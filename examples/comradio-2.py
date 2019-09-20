# -*- coding: utf-8 -*-
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

# This example simulates a simple COM radio like the Bendix/King KY196
# as found in basic planes.
# This example uses the FSMBuilder and the associated YAML file to
# generate a working FSM.

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
# define the user queue to receive callbacks
user_queue = queue.Queue()

# build the FSM from the YAML definition file
builder = pyfsm.FSMBuilder('comradio-2.yml')
obj = builder.parse()
obj.FSM.setup(user_callback, user_queue)
obj.FSM.start()

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
            obj.FSM.update(obj.E4)
        if cmd == 'a':
            obj.FSM.update(obj.E5)

        # increase/decrease decimal part
        if cmd == 'w':
            obj.FSM.update(obj.E6)
        if cmd == 's':
            obj.FSM.update(obj.E7)

        # swap active/standby frequencies
        if cmd == 'u':
            obj.FSM.update(obj.E2)

        # turn on/off the avionics
        if cmd == 'o':
            if avionics_is_on:
                obj.FSM.update(obj.E0)
                avionics_is_on = False
            else:
                obj.FSM.update(obj.E1)
                avionics_is_on = True

        # execute callbacks
        while not user_queue.empty():
            callback = user_queue.get()

            if callback():
                obj.FSM.update(obj.E3)

            user_queue.task_done()

    except pyfsm.FSMError as error:
        print(f"!! {error}")

    except KeyboardInterrupt:
        break

print("")
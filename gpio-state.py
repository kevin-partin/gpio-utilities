#! /usr/bin/env python3

import glob
import os
import sys
import typing

BEAGLEBOARD_BEAGLEBONEBLACK  = 'TI AM335x BeagleBone Black'
BEAGLEBOARD_POCKETBEAGLE = 'TI AM335x PocketBeagle'

def DetermineSBCType() -> str:

    if os.name != 'nt':
        try:
            with open('/proc/device-tree/model', 'rt') as f:
                model = f.read().rstrip('\x00')
        except IOError as exc:
            raise RuntimeError('Host: Unable to determine BeagleBoard model.')
    else:
        model = 'Unknown'

    return model

os.chdir("/sys/class/gpio")

SBC = DetermineSBCType()

if SBC == BEAGLEBOARD_BEAGLEBONEBLACK:

    GPIO2PID: typing.Dict[int, str] = {
         38: 'P8_3',
         39: 'P8_4',
         34: 'P8_5',
         35: 'P8_6',
         66: 'P8_7',
         67: 'P8_8',
         69: 'P8_9',
         68: 'P8_10',
         45: 'P8_11',
         44: 'P8_12',
         23: 'P8_13',
         26: 'P8_14',
         47: 'P8_15',
         46: 'P8_16',
         27: 'P8_17',
         65: 'P8_18',
         22: 'P8_19',
         63: 'P8_20',
         62: 'P8_21',
         37: 'P8_22',
         36: 'P8_23',
         33: 'P8_24',
         32: 'P8_25',
         61: 'P8_26',
         86: 'P8_27',
         88: 'P8_28',
         87: 'P8_29',
         89: 'P8_30',
         10: 'P8_31',
         11: 'P8_32',
          9: 'P8_33',
         81: 'P8_34',
          8: 'P8_35',
         80: 'P8_36',
         78: 'P8_37',
         79: 'P8_38',
         76: 'P8_39',
         77: 'P8_40',
         74: 'P8_41',
         75: 'P8_42',
         72: 'P8_43',
         73: 'P8_44',
         70: 'P8_45',
         71: 'P8_46',
         30: 'P9_11',
         60: 'P9_12',
         31: 'P9_13',
         50: 'P9_14',
         48: 'P9_15',
         51: 'P9_16',
          5: 'P9_17',
          4: 'P9_18',
         13: 'P9_19',
         12: 'P9_20',
          3: 'P9_21',
          2: 'P9_22',
         49: 'P9_23',
         15: 'P9_24',
        117: 'P9_25',
         14: 'P9_26',
        115: 'P9_27',
        113: 'P9_28',
        111: 'P9_29',
        112: 'P9_30',
        110: 'P9_31',
         20: 'P9_41',
        116: 'P9_41.1',
          7: 'P9_42',
        114: 'P9_42.2'
    }

if SBC == BEAGLEBOARD_POCKETBEAGLE:
    pass

PID2GPIO: typing.Dict[str, int] = {}
for gpio, pid in GPIO2PID.items():
    PID2GPIO[pid] = gpio

#------------------------------------------------------------------------------

def filterGPIOState(filter: str) -> dict:

    state = {}

    for gpio in gpioState:

        label, direction, value = gpioState[gpio]

        if filter and filter != direction:
            continue

        state[gpio] = (label, direction, value)

    return state

#------------------------------------------------------------------------------

def getGPIOState(filter: str = None) -> dict:

    state = {}

    for dname in glob.glob("gpio[0-9]*"):

        gpio = int(dname[4:], 10)

        with open(dname + '/label', mode='rt') as f:
            label = f.read().strip()

        with open(dname + '/direction', mode='rt') as f:
            direction = f.read().strip()

        with open(dname + '/value', mode='rt') as f:
            value = int(f.read(), 10)

        if filter and filter != direction:
            continue

        port, bit = divmod(gpio, 32)
        gid = f'GPIO{port}_{bit}'

        state[gpio] = (label, direction, value, port, bit, gid)

    return state

#------------------------------------------------------------------------------

def getMaxLabelLength(state: dict) -> int:

    maxlen = 0

    for gpio in state:

        length = len(state[gpio][0])

        if length > maxlen:
            maxlen = length

    return maxlen

#------------------------------------------------------------------------------

def getMaxPIDLength(state: dict) -> int:

    maxlen = 0

    for gpio in state:

        length = len(GPIO2PID[gpio])

        if length > maxlen:
            maxlen = length

    return maxlen

#------------------------------------------------------------------------------

gpioState = getGPIOState()

MAX_LABEL_LENGTH = getMaxLabelLength(gpioState)
MAX_PID_LENGTH = getMaxPIDLength(gpioState)

if len(sys.argv) == 2:
    pass

while True:

    status = os.system('clear')

    print('\nOutput GPIO States\n')

    for gpio in sorted(gpioState):
        label, direction, value, port, bit, gid = gpioState[gpio]
        if direction == 'out':
            print(f'    {gpio:>3} : {gid:<8s} : {GPIO2PID[gpio]:{MAX_PID_LENGTH}} : {label:{MAX_LABEL_LENGTH}s} : {"H" if value else "L"}')

    try:
        response = input('\nEnter GPIO to toggle: ').strip().lower()
    except KeyboardInterrupt:
        break

    if response == '':
        continue

    if response == 'q':
        break

    gpio = int(response, 10)

    if gpio not in gpioState:
        print('Error: Undefined GPIO:', gpio, file=sys.stderr)
        input('Press any key to continue ...')
        continue

    label, direction, value = gpioState[gpio]

    if direction != 'out':
        print('Error: Unable to toggle GPIO', gpio, file=sys.stderr)
        input('Press any key to continue ...')
        continue

    value = 0 if value else 1

    with open('gpio' + str(gpio) + '/value', mode='wt') as f:
        f.write(str(value))

    gpioState[gpio] = (label, direction, value, port, bit, gid)

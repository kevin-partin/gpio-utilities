#! /usr/bin/env python3

import mmap
import struct

# Valid for BeagleBone Black and PocketBeagle
GPIO_PORT = {

    0: {
        'start-address': 0x44e0_7000,
        'end-address'  : 0x44e0_7fff,
        'size'         : 0x1000
    },

    1: {
        'start-address': 0x4804_c000,
        'end-address'  : 0x4804_cfff,
        'size'         : 0x1000
    },

    2: {
        'start-address': 0x481a_c000,
        'end-address'  : 0x481a_cfff,
        'size'         : 0x1000
    },

    3: {
        'start-address': 0x481a_e000,
        'end-address'  : 0x481a_efff,
        'size'         : 0x1000
    }

}

# Valid for BeagleBone Black and PocketBeagle
GPIO_OE           = 0x134       # Set the appropriate GPIO pin to HIGH for input, and LOW for output
GPIO_DATAIN       = 0x138       # Reading input pins
GPIO_DATAOUT      = 0x13c       # Reading and writing to output pins
GPIO_CLEARDATAOUT = 0x190       # Set the appropriate output pin to LOW
GPIO_SETDATAOUT   = 0x194       # Set the appropriate output pin to HIGH

status = {}

for port in GPIO_PORT:

    print(f'\nPort {port}: GPIO {port * 32} - {((port + 1) * 32) - 1}\n')

    with open("/dev/mem", "r+b" ) as f:

        mem = mmap.mmap(
            fileno = f.fileno(),
            length = GPIO_PORT[port]['size'],
            offset = GPIO_PORT[port]['start-address']
        )

        register = mem[GPIO_OE:GPIO_OE+4]
        status[0] = struct.unpack('<L', register)[0]
        print(f'        OE: 0b{status[0]:032b}')

        register = mem[GPIO_DATAIN:GPIO_DATAIN+4]
        status[1] = struct.unpack('<L', register)[0]
        print(f'    DATAIN: 0b{status[1]:032b}')

        register = mem[GPIO_DATAOUT:GPIO_DATAOUT+4]
        status[2] = struct.unpack('<L', register)[0]
        print(f'   DATAOUT: 0b{status[2]:032b}')

        print()

        for bit in range(32):

            num = (port * 32) + bit

            label = ''
            try:
                with open(f'/sys/class/gpio/gpio{num}/label', 'rt') as l:
                    label = l.read().strip()
            except Exception as exc:
                pass

            # print(f'{num:3d} : {port} : {bit:2d} : GPIO{port}_{bit:<2d} : {status[0] & 1} : {status[1] & 1} : {status[2] & 1}')

            print(f'    {num:3d} : {port} : {bit:2d} : GPIO{port}_{bit:<2d} : {"in " if (status[0] & 1) else "out"} : ', end='')
            if (status[0] & 1):
                print(f'{"H" if (status[1] & 1) else "L"} : {label}')
            else:
                print(f'{"H" if (status[2] & 1) else "L"} : {label}')

            status[0] >>= 1
            status[1] >>= 1
            status[2] >>= 1

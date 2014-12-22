#!/usr/bin/python

# This is a list of esc/pos compatible usb printers. The vendor and product ids can be found by
# typing lsusb in a linux terminal, this will give you the ids in the form ID VENDOR:PRODUCT

device_list = [
    { 'vendor' : 0x04b8, 'product' : 0x0e03, 'name' : 'Epson TM-T20' },
    { 'vendor' : 0x04b8, 'product' : 0x0202, 'name' : 'Epson TM-T70' },
    { 'vendor' : 0x04b8, 'product' : 0x0e15, 'name' : 'Epson TM-T20II' },
    { 'vendor' : 0x04b8, 'product' : 0x0e15, 'name' : 'Epson TM-T20II' },
    { 'vendor' : 0x1504, 'product' : 0x0006, 'name' : 'BIXOLON SRP-350plus' },
    { 'vendor' : 0x0525, 'product' : 0xa700, 'name' : 'Netchip Tech., Inc. MicroPOS WTP-100ESC' },
]


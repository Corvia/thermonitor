#!/usr/bin/python

"""
Emulate the output of the digitemp_DS9097 for testing purposes.
"""

import random
import decimal

guids = [
    "286FCB8205000040",
    "286FCB8205000041",
    "286FCB8205000042",
    "286FCB8205000043",
    "286FCB8205000044",
    "286FCB8205000045",
    "286FCB8205000046",
    "286FCB8205000047",
    "286FCB8205000048",
    "286FCB8205000049",
]

for guid in guids:
    temperature = round(decimal.Decimal(str(random.random())) * 100, 1)
    print "%s %s" % (guid, temperature)
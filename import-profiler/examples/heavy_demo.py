# Simulate heavy module init
total = 0
for i in range(20000):
    total += i * 2  # ~20ms excl on avg machine

import os  # ~1ms incl
import sys
print("Heavy demo loaded", total)

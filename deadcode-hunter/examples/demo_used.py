# All used - no issues

import os
print(os.getcwd())

from math import pi
print(pi)

used_global = "hello"
print(used_global)

def used():
    pass
used()

class Used:
    pass
print(Used)
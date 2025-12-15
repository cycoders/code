# Demo: Run 'python -m deadcode_hunter scan examples/'

import unused_lib1  # DETECTED: unused_import 90%
import unused_lib2.sub  # DETECTED

from unused_pkg import unused_func  # DETECTED

unused_var = 42  # DETECTED: unused_variable 70%

class UnusedClass:  # DETECTED: unused_class 80%
    pass

def unused_function():  # DETECTED
    pass

# Used:
import sys
print(sys.version)

used_var = 1
print(used_var)

def used_func():
    pass
used_func()
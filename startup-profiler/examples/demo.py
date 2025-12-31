#!/usr/bin/env python3
"""Demo script for startup-profiler."""
import os
import sys  # stdlib ~1ms
import time  # simulate slow init
time.sleep(0.002)  # 2ms
print("[demo] Startup imports complete")

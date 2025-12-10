#!/usr/bin/env python3
"""
Pokemon Info CLI - Fetch details from PokeAPI.
"""
import os
import sys

# Allow imports from src/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import run

if __name__ == '__main__':
    run()

# Messy imports example
import random  # third
from typing import Dict, Any  # stdlib
import os  # stdlib unused
from .models import User  # local
import requests  # third unused
print(requests.get(''))
print(os.getcwd())
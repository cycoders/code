import threading
shared = []

def worker():
    shared.append(1)  # unprotected

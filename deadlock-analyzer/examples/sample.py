import threading
lock_a = threading.Lock()
lock_b = threading.Lock()

def task1():
    with lock_a:
        with lock_b:
            pass

def task2():
    with lock_b:
        with lock_a:
            pass
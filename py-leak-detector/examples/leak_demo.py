import time

data = []

print("Starting leaky loop... Ctrl+C to stop")
while True:
    # Leak: growing list of 1MB chunks
    data.append([0] * (1024 * 256))  # ~1MB
    time.sleep(0.2)

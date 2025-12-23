import sys
import time
import random

ALGO = sys.argv[1] if len(sys.argv) > 1 else "bubble"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 1000

print(f"Sorting {N} items with {ALGO} sort...")

arr = list(range(N))
random.shuffle(arr)

if ALGO == "bubble":
    for i in range(N):
        for j in range(0, N - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
elif ALGO == "insertion":
    for i in range(1, N):
        key = arr[i]
        j = i - 1
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key

print("Done.")
assert arr == list(range(N))
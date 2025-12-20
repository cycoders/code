import time

print("Stable loop: recomputing pi approx")
def approx_pi(n):
    return sum((-1)**k / (2*k + 1) for k in range(n))

i = 0
while True:
    pi = approx_pi(10000)
    print(f"{i}: pi ~ {pi:.5f}")
    i += 1
    time.sleep(0.5)

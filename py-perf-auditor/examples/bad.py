# Example of detected pitfalls

s = ""
for i in range(1000):
    s += str(i)  # Detected: string-concat-loop
    s = s + f"{i}"  # Also detected

l1 = [1] * 10
l2 = [2] * 10
combined = l1 + l2  # list-concat

numbers = list(map(str, range(100)))  # list-on-map-filter

keys = list(my_dict.keys())  # list-dict-keys

print("All pitfalls above should be flagged!")
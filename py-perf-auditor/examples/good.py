# No pitfalls here

parts = []
for i in range(1000):
    parts.append(str(i))
s = "".join(parts)

l1 = [1] * 10
l1.extend([2] * 10)

gens = (str(i) for i in range(100))
# list(gens)  # Avoided!

for k in my_dict:
    pass

print("Clean code!")
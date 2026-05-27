from ulid_toolkit.core import generate, parse

u = generate(monotonic=True)
print(parse(str(u)))
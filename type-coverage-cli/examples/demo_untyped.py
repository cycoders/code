# Example: Mixed coverage
def untyped():
    pass

def partial(x, y: int):
    return x + y

def full(a: str, b: int) -> bool:
    return len(a) > b

class Partial:
    def no_ann(self):
        pass

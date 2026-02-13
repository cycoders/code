def fibonacci(n: int) -> int:
    """Slow recursive fib for profiling demo."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


if __name__ == "__main__":
    result = fibonacci(32)
    print(f"fib(32) = {result}")

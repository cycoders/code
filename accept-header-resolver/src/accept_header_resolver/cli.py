import argparse
from .resolver import resolve

def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve Accept header")
    parser.add_argument("header", help="Accept header value")
    parser.add_argument("offered", nargs="+", help="Offered media types")
    args = parser.parse_args()
    result = resolve(args.header, args.offered)
    print(result.offered if result else "no match")

if __name__ == "__main__":
    main()
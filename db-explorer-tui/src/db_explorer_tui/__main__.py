import sys

from db_explorer_tui.app import DBExplorer


def main():
    dsn = sys.argv[1] if len(sys.argv) > 1 else None
    app = DBExplorer(dsn=dsn)
    app.run()


if __name__ == "__main__":
    main()
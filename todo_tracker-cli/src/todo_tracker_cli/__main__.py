'''CLI entrypoint for running as `python -m todo_tracker_cli`.'''

from .cli import app

if __name__ == "__main__":
    app(prog_name="todo-tracker")
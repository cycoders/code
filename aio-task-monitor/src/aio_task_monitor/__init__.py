__version__ = "0.1.0"


def start_monitoring() -> None:
    """
    Start the TUI monitor in a background daemon thread.

    Call this early in your asyncio app, e.g. before `asyncio.run(main())`.

    Example::

        from aio_task_monitor import start_monitoring
        start_monitoring()
        asyncio.run(main())
    """
    import threading

    def _run_monitor():
        from .cli import app
        import sys
        sys.argv = ['aio-task-monitor', 'monitor']  # Simulate CLI
        app(standalone_mode=False)

    thread = threading.Thread(target=_run_monitor, daemon=True)
    thread.start()
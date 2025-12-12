import argparse
from .app import HeatmapApp

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real-time process CPU/memory heatmap monitor")
    parser.add_argument("--top", type=int, default=40, help="Maximum number of top processes to display")
    parser.add_argument("--interval", type=float, default=1.0, help="Update interval in seconds (min 0.1)")
    parser.add_argument("--cpu-thresh", type=float, default=0.0, help="Minimum CPU percentage to include process")
    args = parser.parse_args()
    if args.interval < 0.1:
        args.interval = 0.1
    app = HeatmapApp(top=args.top, interval=args.interval, cpu_thresh=args.cpu_thresh)
    app.run()
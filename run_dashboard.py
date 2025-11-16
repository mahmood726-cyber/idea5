#!/usr/bin/env python3
"""
Launch the Publication Bias Assessment Dashboard.

Usage:
    python run_dashboard.py [--port PORT] [--debug]
"""

import argparse
from src.dashboard import create_dashboard


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Method Publication Bias Assessment Dashboard"
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8050,
        help='Port number for the dashboard server (default: 8050)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Run in debug mode'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Host address (default: 127.0.0.1)'
    )

    args = parser.parse_args()

    print("="* 70)
    print("Multi-Method Publication Bias Assessment Dashboard")
    print("=" * 70)
    print(f"\nStarting dashboard on http://{args.host}:{args.port}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70)

    # Create and run dashboard
    dashboard = create_dashboard()
    dashboard.app.run_server(
        debug=args.debug,
        port=args.port,
        host=args.host
    )


if __name__ == '__main__':
    main()

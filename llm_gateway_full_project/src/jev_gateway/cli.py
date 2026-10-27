"""Command line entry point."""

import argparse


def main(argv=None):
    parser = argparse.ArgumentParser(prog="jev", description="Jev text chat gateway")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("serve", help="serve the gateway")
    sub.add_parser("doctor", help="check configuration and backends")
    sub.add_parser("smoke", help="send one bounded chat request")
    args = parser.parse_args(argv)
    if args.command == "serve":
        import uvicorn
        uvicorn.run("jev_gateway.api:app", host="127.0.0.1", port=8080)
    elif args.command == "doctor":
        from .diagnostics import doctor
        return doctor()
    elif args.command == "smoke":
        from .diagnostics import smoke
        return smoke()


if __name__ == "__main__":
    raise SystemExit(main())

"""Command line entry point."""

import argparse


def main(argv=None):
    parser = argparse.ArgumentParser(prog="jev", description="Jev text chat gateway")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("serve", help="serve the gateway")
    sub.add_parser("doctor", help="check configuration and backends")
    smoke_parser = sub.add_parser("smoke", help="send one bounded chat request")
    smoke_parser.add_argument("--tier", choices=("small", "medium", "frontier"), default="small")
    smoke_parser.add_argument("--gateway-url", default="http://127.0.0.1:8080")
    args = parser.parse_args(argv)
    if args.command == "serve":
        import uvicorn
        uvicorn.run("jev_gateway.api:app", host="127.0.0.1", port=8080)
    elif args.command == "doctor":
        from .diagnostics import doctor
        return doctor()
    elif args.command == "smoke":
        from .diagnostics import smoke
        return smoke(args.tier, args.gateway_url)


if __name__ == "__main__":
    raise SystemExit(main())

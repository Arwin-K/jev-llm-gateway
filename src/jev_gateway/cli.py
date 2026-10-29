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
    sub.add_parser("eval-prepare", help="download pinned benchmark snapshots and freeze manifest")
    run = sub.add_parser("eval-run", help="bounded development tier evaluation")
    run.add_argument("--split", choices=("train", "validation"), default="validation")
    run.add_argument("--tier", choices=("small", "medium", "frontier"), action="append", required=True)
    run.add_argument("--max-prompts", type=int, required=True)
    run.add_argument("--max-requests", type=int, required=True)
    run.add_argument("--max-tokens", type=int, required=True)
    run.add_argument("--max-usd", type=float, default=0)
    run.add_argument("--output-tokens", type=int, default=128)
    run.add_argument("--concurrency", type=int, default=1)
    run.add_argument("--retries", type=int, default=0)
    run.add_argument("--paid-enabled", action="store_true")
    run.add_argument("--rate-file", help="dated sourced JSON API rates")
    report = sub.add_parser("eval-report", help="report saved quality observations")
    report.add_argument("--run", required=True)
    report.add_argument("--split", choices=("train", "validation"), default="validation")
    audit = sub.add_parser("eval-audit", help="export private pending-review CSV")
    audit.add_argument("--run", required=True)
    audit.add_argument("--split", choices=("train", "validation"), default="validation")
    serving = sub.add_parser("eval-serving", help="bounded client streaming baseline")
    serving.add_argument("--tier", choices=("small", "medium", "frontier"), required=True)
    serving.add_argument("--prompt", required=True)
    serving.add_argument("--requests", type=int, required=True)
    serving.add_argument("--arrival-interval", type=float, default=0)
    serving.add_argument("--concurrency", type=int, default=1)
    serving.add_argument("--output-tokens", type=int, default=128)
    serving.add_argument("--warmup", type=int, default=0)
    serving.add_argument("--cache-state", default="off")
    serving.add_argument("--placement", default="unknown")
    serving.add_argument("--model-condition", choices=("cold","warm","unverified"), default="unverified")
    serving.add_argument("--max-usd", type=float, default=0)
    serving.add_argument("--paid-enabled", action="store_true")
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
    else:
        from .evaluation.commands import execute
        return execute(args)


if __name__ == "__main__":
    raise SystemExit(main())

"""Command line entry point."""

import argparse


def main(argv=None):
    parser = argparse.ArgumentParser(prog="laya-gateway", description="Local model routing with native Laya decisions")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="check configuration and backends")
    chat = sub.add_parser("chat", help="route and generate one local response")
    chat.add_argument("prompt")
    chat.add_argument("--model", choices=("small", "medium", "auto"), default="auto")
    chat.add_argument("--max-tokens", type=int)
    smoke_parser = sub.add_parser("smoke", help="send one bounded local chat request")
    smoke_parser.add_argument("--tier", choices=("small", "medium", "auto"), default="auto")
    prepare = sub.add_parser("eval-prepare", help="download pinned benchmark snapshots and freeze manifest")
    prepare.add_argument("--offline", action="store_true", help="rebuild from existing data/day2_sources snapshots")
    prepare.add_argument("--previous", help="earlier manifest whose prompt IDs and splits must be unchanged")
    run = sub.add_parser("eval-run", help="bounded development tier evaluation")
    run.add_argument("--split", choices=("train", "validation"), default="validation")
    run.add_argument("--task", choices=("math", "choice", "code"), action="append", help="include only these task types; repeat to select more than one")
    run.add_argument("--prompt-id", action="append", help="include only these exact manifest prompt IDs; repeat for more than one")
    run.add_argument("--tier", choices=("small", "medium", "frontier"), action="append", required=True)
    run.add_argument("--max-prompts", type=int, required=True)
    run.add_argument("--max-requests", type=int, required=True)
    run.add_argument("--max-tokens", type=int, required=True)
    run.add_argument("--max-usd", type=float, default=0)
    run.add_argument("--output-tokens", type=int, default=512)
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
    if args.command == "doctor":
        from .diagnostics import doctor
        return doctor()
    elif args.command == "smoke":
        from .diagnostics import smoke
        return smoke(args.tier)
    elif args.command == "chat":
        from .chat import complete_local
        from .config import from_env
        import asyncio
        try:
            result = asyncio.run(complete_local(from_env(), args.prompt, tier=args.model,
                                                max_tokens=args.max_tokens))
        except (ValueError, RuntimeError) as exc:
            parser.error(str(exc))
        print(result.answer)
        return 0
    else:
        from .evaluation.commands import execute
        return execute(args)


if __name__ == "__main__":
    raise SystemExit(main())

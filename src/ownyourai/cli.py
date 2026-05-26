"""`oya` — own-your-ai CLI entry point."""

import argparse
import sys

from . import __version__
from .commands import audit, export, init, sign, verify


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oya",
        description="own-your-ai — Your AI. Your data. Your rules.",
    )
    parser.add_argument("--version", action="version", version=f"oya {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)
    init.register(subparsers)
    sign.register(subparsers)
    verify.register(subparsers)
    audit.register(subparsers)
    export.register(subparsers)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

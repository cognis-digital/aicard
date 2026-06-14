"""Command-line interface for AICARD.

Subcommands:
  check  - evaluate a descriptor against NIST AI RMF / EU AI Act Annex IV
           disclosure requirements (default).
  card   - render a Markdown model/system card from a descriptor.

Exit codes:
  0  no blocking findings
  1  one or more blocking findings (compliance gate failed)
  2  usage / input error
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from . import TOOL_NAME, TOOL_VERSION
from .core import (
    load_descriptor,
    evaluate,
    render_card,
    render_report_table,
    report_to_dict,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=TOOL_NAME,
        description="Auto-generate and lint NIST AI RMF / EU AI Act Annex IV "
                    "model & system cards from a JSON descriptor.",
        epilog="Example: aicard check demos/01-basic/system.json --format json",
    )
    parser.add_argument("--version", action="version",
                        version=f"{TOOL_NAME} {TOOL_VERSION}")
    sub = parser.add_subparsers(dest="command")

    chk = sub.add_parser("check",
                         help="evaluate a descriptor and report findings")
    chk.add_argument("descriptor", help="path to the system descriptor JSON")
    chk.add_argument("--format", choices=["table", "json"], default="table",
                     help="output format (default: table)")

    card = sub.add_parser("card",
                          help="render a Markdown model card from a descriptor")
    card.add_argument("descriptor", help="path to the system descriptor JSON")
    card.add_argument("--format", choices=["table", "json"], default="table",
                      help="'table' emits Markdown card; 'json' wraps it")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    try:
        descriptor = load_descriptor(args.descriptor)
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report = evaluate(descriptor)

    if args.command == "check":
        if args.format == "json":
            print(json.dumps(report_to_dict(report), indent=2))
        else:
            print(render_report_table(report))
        return 0 if report.compliant else 1

    if args.command == "card":
        markdown = render_card(report)
        if args.format == "json":
            payload = report_to_dict(report)
            payload["card_markdown"] = markdown
            print(json.dumps(payload, indent=2))
        else:
            print(markdown)
        return 0 if report.compliant else 1

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

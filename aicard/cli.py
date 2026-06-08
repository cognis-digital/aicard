"""AICARD command-line interface."""
from cognis_core import build_cli
from aicard.core import scan, TOOL_NAME, TOOL_VERSION

main = build_cli(
    tool_name=TOOL_NAME,
    tool_version=TOOL_VERSION,
    description="Auto-generated NIST AI RMF / EU AI Act Annex IV model & system cards",
    scan_fn=scan,
)

if __name__ == "__main__":
    import sys
    sys.exit(main())

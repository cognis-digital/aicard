# AICARD — Auto-generated NIST AI RMF / EU AI Act Annex IV model & system cards

> Part of the **[Cognis Neural Suite](https://github.com/cognis-digital)** by [Cognis Digital](https://cognis.digital)
> Cognis Open Collaboration License (COCL) v1.0 · domain: `ai-security`

[![PyPI](https://img.shields.io/pypi/v/cognis-aicard.svg)](https://pypi.org/project/cognis-aicard/)
[![CI](https://github.com/cognis-digital/aicard/actions/workflows/ci.yml/badge.svg)](https://github.com/cognis-digital/aicard/actions)
[![License: COCL 1.0](https://img.shields.io/badge/License-COCL%201.0-2b6cb0.svg)](LICENSE)
[![Suite](https://img.shields.io/badge/Cognis-Neural%20Suite-6b46c1.svg)](https://github.com/cognis-digital)

**Auto-generated NIST AI RMF / EU AI Act Annex IV model & system cards.**

*AI Security & Governance — securing LLMs, agents, and the MCP supply chain.*

## Why

Security and intelligence teams need auto-generated NIST AI RMF / EU AI Act Annex IV model & system cards without standing up heavyweight infrastructure. `aicard` is single-purpose, scriptable, CI-friendly, and self-hostable: point it at a target, get prioritized findings in the format your workflow already speaks (table, JSON, SARIF, HTML), and wire it into agents over MCP when you want it autonomous.

## Install

```bash
pip install cognis-aicard
# or, from this repo:
pip install -e ".[dev]"
```

## Quick start

```bash
aicard --version
aicard scan demos/                      # run against the bundled demo
aicard scan demos/ --format sarif --out r.sarif --fail-on high
aicard scan demos/ --format html --out report.html
aicard mcp                              # expose as an MCP server (Cognis.Studio / Claude Desktop / Cursor)
```

## Built-in demo scenarios

Each scenario folder includes a `SCENARIO.md` describing the situation and the findings to expect.

- [`demos/01-basic/`](demos/01-basic/SCENARIO.md)
- [`demos/01-eu-ai-act-high-risk/`](demos/01-eu-ai-act-high-risk/SCENARIO.md)
- [`demos/02-medical-llm-complete/`](demos/02-medical-llm-complete/SCENARIO.md)
- [`demos/03-internal-chatbot/`](demos/03-internal-chatbot/SCENARIO.md)

## Output formats

- **Table** (default) — human-readable terminal summary
- **JSON** — machine-readable findings for pipelines
- **SARIF** — drops into GitHub code-scanning / IDE problem panes
- **HTML** — shareable report with severity rollups

## How it fits the Cognis Neural Suite

`aicard` is one of **52 tools** in the [Cognis Neural Suite](https://github.com/cognis-digital). Every tool ships an MCP server, so [Cognis.Studio](https://cognis.studio) agents can call them as scoped capabilities.

**Sibling tools in `ai-security`:** [`aegis`](https://github.com/cognis-digital/aegis), [`promptmirror`](https://github.com/cognis-digital/promptmirror), [`ledgermind`](https://github.com/cognis-digital/ledgermind), [`adversa`](https://github.com/cognis-digital/adversa), [`guardpost`](https://github.com/cognis-digital/guardpost), [`hallumark`](https://github.com/cognis-digital/hallumark), [`biascope`](https://github.com/cognis-digital/biascope), [`mcpharden`](https://github.com/cognis-digital/mcpharden), [`agentlog`](https://github.com/cognis-digital/agentlog), [`ragshield`](https://github.com/cognis-digital/ragshield)

## Architecture & roadmap

- Design notes: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Planned work: [`ROADMAP.md`](ROADMAP.md)

## Contributing

PRs, new detections, and demo scenarios are welcome under the collaboration-pull model. See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## License

Source-available under the **Cognis Open Collaboration License (COCL) v1.0** — free for personal, internal-evaluation, research, and educational use; **commercial / production use requires a license** (licensing@cognis.digital). See [LICENSE](LICENSE).

## Responsible use

This is dual-use security software. Use it only against systems, data, and identities you own or are explicitly authorized in writing to test, and in compliance with applicable law.

## About

**[Cognis Digital](https://cognis.digital)** — Wyoming, USA · *Making Tomorrow Better Today: Advanced Cybersecurity, AI Innovation, and Blockchain Expertise.*

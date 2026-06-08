# AICARD — Auto-generated NIST AI RMF / EU AI Act Annex IV model & system cards

> Part of the **[Cognis Neural Suite](https://github.com/cognis-digital)** by [Cognis Digital](https://cognis.digital)
> Cognis Open Collaboration License (COCL) v1.0 · domain: `ai-security`

[![PyPI](https://img.shields.io/pypi/v/cognis-aicard.svg)](https://pypi.org/project/cognis-aicard/)
[![CI](https://github.com/cognis-digital/aicard/actions/workflows/ci.yml/badge.svg)](https://github.com/cognis-digital/aicard/actions)
[![License: COCL 1.0](https://img.shields.io/badge/License-COCL%201.0-2b6cb0.svg)](LICENSE)

Auto-generated NIST AI RMF / EU AI Act Annex IV model & system cards.

## Install

```bash
pip install cognis-aicard
```

For local development from this repo:

```bash
pip install -e .
```

## Quick start

```bash
aicard --version
aicard scan demos/                          # run against bundled demo
aicard scan demos/ --format sarif --out r.sarif --fail-on high
aicard mcp                                   # start as MCP server (Cognis.Studio / Claude Desktop / Cursor)
```

## Built-in demo scenarios

Every scenario folder includes a `SCENARIO.md` describing what it represents and what findings to expect.

- `demos/01-eu-ai-act-high-risk/` — see [`SCENARIO.md`](demos/01-eu-ai-act-high-risk/SCENARIO.md)
- `demos/02-medical-llm-complete/` — see [`SCENARIO.md`](demos/02-medical-llm-complete/SCENARIO.md)
- `demos/03-internal-chatbot/` — see [`SCENARIO.md`](demos/03-internal-chatbot/SCENARIO.md)

## How it fits the Cognis Neural Suite

This tool is one of 52 in the [Cognis Neural Suite](https://github.com/cognis-digital). The full suite + launcher lives at:

- Suite landing: https://cognis.digital
- All 52 repos: https://github.com/cognis-digital
- Cognis.Studio (Enterprise AI Workforce, MCP host): https://cognis.studio

Every Suite tool ships an MCP server, so Cognis.Studio agents can call them as scoped capabilities.

## License

Source-available under the **Cognis Open Collaboration License (COCL) v1.0** — free for personal, internal-evaluation, research, and educational use; **commercial / production use requires a license** (licensing@cognis.digital). See [LICENSE](LICENSE) and [CONTRIBUTING.md](CONTRIBUTING.md) for the collaboration-pull model.

## About

**[Cognis Digital](https://cognis.digital)** — Wyoming, USA · *Making Tomorrow Better Today: Advanced Cybersecurity, AI Innovation, and Blockchain Expertise.*

# Demo 16 - RAG support copilot (GenAI, fully compliant)

**Where the data came from:** a SaaS support org documenting a
retrieval-augmented LLM that drafts replies for human agents. It captures the
GenAI-specific risks: hallucination, cross-tenant data leakage, and prompt
injection.

**What to expect:** every catalogued disclosure is present and substantive, so
`check` reports **100% coverage, 0 blockers, 0 warnings** and exits **0**. The
generated card doubles as the system's responsible-AI fact sheet.

## Run it

```bash
python -m aicard check demos/16-genai-support-copilot/support_copilot.json
python -m aicard card  demos/16-genai-support-copilot/support_copilot.json > COPILOT_CARD.md
```

## How to act

Use this as the template for documenting a RAG / agent-assist feature: note
the groundedness + hallucination metrics in `measure.metrics`, the red-team
prompt-injection suite in `measure.test_data`, and the per-tenant retrieval
isolation in `manage.mitigations`. These are the disclosures auditors ask for
on generative systems.

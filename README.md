# strands-evals

Working through [Strands /evals Quickstart](https://strandsagents.com/docs/user-guide/evals-sdk/quickstart/)

## Setup

Evals run against [OpenRouter](https://openrouter.ai/) (OpenAI-compatible). Provide an API key either via your environment:

```bash
export OPENROUTER_API_KEY=sk-or-...
```

or by copying `.env.example` to `.env` and filling it in (loaded automatically on startup).

## Running

```bash
uv run strands-investig basic-eval
```

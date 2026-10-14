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

## Running strands-decider

Serve a decider model locally:

```bash
uv run strands-decider serve StrandsAgents/strands-decider-2B-hobson-v19 --port 14435
```

Or ask the 2B decider model to decide something directly:

```bash
uv run strands-investig decider
```

### `strands-investig` commands and model downloads

`strands-investig <command>` ([src/strands_investig/\_\_init\_\_.py](src/strands_investig/__init__.py))
dispatches to a module per command; run with no command to see the current list.

`decider` loads `StrandsAgents/strands-decider-2B-hobson-v19` plus its base model
(`Qwen/Qwen3.5-2B-Base`) from the Hugging Face Hub cache, downloading both the first time it
runs. That first run can be slow (or fail if you're offline), so to fetch the weights ahead of
time without loading them onto a device, run:

```bash
uv run strands-investig download-decider
```

After that, `decider` loads straight from the local Hugging Face cache.

Both commands use the standard Hugging Face Hub cache — `$HF_HOME/hub` if `HF_HOME` is set,
otherwise `~/.cache/huggingface/hub`. That cache is shared across every project and tool on
the machine that uses Hugging Face models, not just this one, and together the two downloads
are several GB.

To remove what this project has added — the decider checkpoint and base model from the
Hugging Face cache (other repos in that cache are left alone), plus the local
`basic_evaluation.json` / `generated_experiment.json` files written by `basic-eval` /
`experiment-generation` — run:

```bash
uv run strands-investig clean
```

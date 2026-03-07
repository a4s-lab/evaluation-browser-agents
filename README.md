# Evaluation Browser Agents

Quick evaluation of browser agents, inspired by [WebVoyager](https://github.com/MinorJerry/WebVoyager).

## Result

| Agent | Model | Overall | Cost |
| --- | --- | --- | --- |
| [smooth](https://www.smooth.sh/) | smooth | 11/26 (42.3%) | $2.15 |

## Usage

### Prerequisites

```bash
cp .env.example .env
# Fill in your API keys in .env
```

### browser-use

```bash
# Run all tasks
uv run --env-file .env scripts/eval_browser_use.py --model gpt-4o --headless

# Run specific tasks
uv run --env-file .env scripts/eval_browser_use.py --model gpt-4o --task-id "Wolfram Alpha--1"

# Use Anthropic models
uv run --env-file .env scripts/eval_browser_use.py --model claude-sonnet-4-20250514

# Use OpenRouter
uv run --env-file .env scripts/eval_browser_use.py --provider openrouter --model "deepseek/deepseek-v3.2"

# Show browser window
uv run --env-file .env scripts/eval_browser_use.py --model gpt-4o --no-headless --max-steps 50
```

Results are saved to `results/browser-use.jsonl`.

### smooth

CIRCLEMIND_API_KEY should be set for smooth agent. Please refer to the [Smooth](https://docs.smooth.sh/quickstart) for more information.

```bash
# Run all tasks
uv run --env-file .env scripts/eval_smooth.py

# Run specific tasks
uv run --env-file .env scripts/eval_smooth.py --task-id "Wolfram Alpha--1"

# Use smooth-lite agent
uv run --env-file .env scripts/eval_smooth.py --model smooth-lite

# Enable stealth mode
uv run --env-file .env scripts/eval_smooth.py --stealth-mode --max-steps 64
```

Results are saved to `results/smooth.jsonl`.

## Evaluation Dataset

Sampled 26 tasks from [WebVoyager](https://github.com/MinorJerry/WebVoyager).

| Website | Easy | Medium | Hard | Total |
| --- | --- | --- | --- | --- |
| Wolfram Alpha | 2 | 1 | - | 3 |
| Google Map | 1 | 2 | - | 3 |
| BBC News | 1 | 2 | - | 3 |
| ArXiv | 2 | 1 | - | 3 |
| Allrecipes | 1 | 2 | - | 3 |
| Amazon | 1 | 1 | 1 | 3 |
| GitHub | 2 | 1 | - | 3 |
| Google Search (GAIA) | - | 2 | 3 | 5 |

### By difficulty

- **Easy: 10** - single-step lookups, simple queries
- **Medium: 11** - multi-constraint filters, comparisons
- **Hard: 5** - multi-step reasoning, cross-source

### By task type

- **lookup: 11** - find specific info on a page
- **filter: 7** - search with constraints (rating, price, date)
- **compare: 2** - compare values across sections
- **compute: 3** - calculation using web-sourced data
- **multi-step: 3** - chain multiple searches/reasoning

### By answer type

- **exact_match: 22** - exact-match evaluation possible
- **llm_judge: 4** - needs GPT-4V judge

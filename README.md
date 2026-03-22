# Evaluation Browser Agents

Quick evaluation of browser agents, inspired by [WebVoyager](https://github.com/MinorJerry/WebVoyager).

## Result with [sample 26 tasks](#sample-26-tasks)

| Agent                                                     | Model                  | Overall       | Environment  | Cost  | Duration | Result                                         |
| --------------------------------------------------------- | ---------------------- | ------------- | ------------ | ----- | -------- | ---------------------------------------------- |
| [smooth](https://www.smooth.sh/)                          | smooth                 | 19/26 (73.1%) | smooth cloud | $2.15 | 11s      | [result](results/smooth-1772886148.jsonl)      |
| [browser-use](https://github.com/browser-use/browser-use) | qwen/qwen3.5-122b-a10b | 16/26 (61.5%) | local        | <$2.5 | 46m      | [result](results/browser-use-1773118672.jsonl) |
| a4s                                                       | qwen/qwen3.5-122b-a10b | 16/26 (61.5%) | local        | <$4   | 1h 51m   | [result](results/a4s-1773241954.jsonl)         |
| [browser-use](https://github.com/browser-use/browser-use) | qwen3.5-27b            | 15/26 (57.7%) | local        | $2.47 | 1h 55m   | [result](results/browser-use-1773242158.jsonl) |

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

Results are saved to `results/browser-use-<timestamp>.jsonl`.

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

Results are saved to `results/smooth-<timestamp>.jsonl`.

### a4s

```bash
# Run all tasks
uv run --env-file .env scripts/eval_a4s.py --binary /path/to/a4s

# With OpenRouter provider and lite model
uv run --env-file .env scripts/eval_a4s.py --binary /path/to/a4s \
  --provider openrouter --model qwen/qwen3.5-122b-a10b --lite-model openai/gpt-oss-120b:nitro

# Run specific tasks
uv run --env-file .env scripts/eval_a4s.py --binary /path/to/a4s --task-id "Wolfram Alpha--1"

# Show browser window
uv run --env-file .env scripts/eval_a4s.py --binary /path/to/a4s --no-headless --max-steps 100
```

To use [Browserbase](https://www.browserbase.com/) cloud browsers (bypasses anti-bot detection):

```bash
export BROWSERBASE_API_KEY=<your-key>
export BROWSERBASE_PROJECT_ID=<your-project-id>
uv run --env-file .env scripts/eval_a4s.py --binary /path/to/a4s \
  --provider openrouter --model qwen/qwen3.5-122b-a10b --lite-model openai/gpt-oss-120b:nitro \
  --no-headless
```

Results are saved to `results/a4s-<timestamp>.jsonl`.

## Evaluation Dataset

### Sample 26 tasks

Sampled 26 tasks from [WebVoyager](https://github.com/MinorJerry/WebVoyager).

| Website              | Easy | Medium | Hard | Total |
| -------------------- | ---- | ------ | ---- | ----- |
| Wolfram Alpha        | 2    | 1      | -    | 3     |
| Google Map           | 1    | 2      | -    | 3     |
| BBC News             | 1    | 2      | -    | 3     |
| ArXiv                | 2    | 1      | -    | 3     |
| Allrecipes           | 1    | 2      | -    | 3     |
| Amazon               | 1    | 1      | 1    | 3     |
| GitHub               | 2    | 1      | -    | 3     |
| Google Search (GAIA) | -    | 2      | 3    | 5     |

#### By difficulty

- **Easy: 10** - single-step lookups, simple queries
- **Medium: 11** - multi-constraint filters, comparisons
- **Hard: 5** - multi-step reasoning, cross-source

#### By task type

- **lookup: 11** - find specific info on a page
- **filter: 7** - search with constraints (rating, price, date)
- **compare: 2** - compare values across sections
- **compute: 3** - calculation using web-sourced data
- **multi-step: 3** - chain multiple searches/reasoning

### Full Dataset

481 tasks across 14 websites from [WebVoyager](https://github.com/MinorJerry/WebVoyager).

| Website        | Easy | Medium | Hard | Total |
| -------------- | ---- | ------ | ---- | ----- |
| Allrecipes     | 6    | 29     | 4    | 39    |
| Amazon         | 6    | 23     | 9    | 38    |
| Apple          | 20   | 12     | -    | 32    |
| ArXiv          | 18   | 17     | 6    | 41    |
| BBC News       | 12   | 20     | 3    | 35    |
| Booking        | 5    | 6      | -    | 11    |
| Coursera       | 8    | 30     | 2    | 40    |
| ESPN           | 22   | 16     | 2    | 40    |
| GitHub         | 21   | 19     | -    | 40    |
| Google Flights | 5    | 3      | -    | 8     |
| Google Map     | 20   | 15     | 3    | 38    |
| Google Search  | 28   | 6      | 6    | 40    |
| Huggingface    | 13   | 20     | -    | 33    |
| Wolfram Alpha  | 27   | 17     | 2    | 46    |

#### By difficulty

- **Easy: 211 (43.9%)** - single-step lookups, simple queries
- **Medium: 233 (48.4%)** - multi-constraint filters, comparisons
- **Hard: 37 (7.7%)** - multi-step reasoning, cross-source

#### By task type

- **lookup: 283 (58.8%)** - find specific info on a page
- **filter: 145 (30.1%)** - search with constraints (rating, price, date)
- **compute: 28 (5.8%)** - calculation using web-sourced data
- **multi-step: 14 (2.9%)** - chain multiple searches/reasoning
- **compare: 11 (2.3%)** - compare values across sections

### Evaluation

All tasks are evaluated using an LLM judge (GPT-4o by default).

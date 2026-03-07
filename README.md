# Evaluation Browser Agents

Quick evaluation of browser agents, inspired by [WebVoyager](https://github.com/MinorJerry/WebVoyager).

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

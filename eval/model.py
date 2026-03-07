from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


def load_tasks(path: str = "tasks.jsonl") -> list[Task]:
    """Load tasks from a JSONL file."""
    with open(path) as f:
        return [Task.model_validate_json(line) for line in f if line.strip()]


class Task(BaseModel):
    # Unique task identifier
    id: str
    # The question or instruction for the agent
    task: str
    # Reference answer for evaluation
    answer: str
    # Name of the target website (e.g. "Google Map")
    web_title: str
    # Starting URL for the task
    web_url: str
    # Task difficulty level
    # easy: single-step lookups, simple queries
    # medium: multi-constraint filters, comparisons
    # hard: multi-step reasoning, cross-source
    level: Literal["easy", "medium", "hard"]
    # lookup: find specific info on a page
    # filter: search with constraints (rating, price, date)
    # compare: compare values across sections
    # compute: calculation using web-sourced data
    # multi-step: chain multiple searches/reasoning
    task_type: Literal["lookup", "filter", "compare", "compute", "multi-step"]
    # exact_match: exact-match evaluation possible
    # llm_judge: needs VLM judge
    answer_type: Literal["exact_match", "llm_judge"]


class EvaluationResult(BaseModel):
    # Unique evaluation identifier
    task_id: str
    # Name of the agent (e.g. "browser-use")
    agent: str
    # Model used (e.g. "gpt-4o")
    model: str
    # Agent's raw answer
    answer: str
    # Correctness
    is_correct: bool
    # Explanation from judge (only if llm_judge)
    reason: str | None
    # Performance metrics
    steps: int
    duration_seconds: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

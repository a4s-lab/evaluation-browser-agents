from typing import Literal

from pydantic import BaseModel


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

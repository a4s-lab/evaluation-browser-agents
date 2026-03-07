# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "eval",
#   "smooth-py",
# ]
# [tool.uv.sources]
# eval = { path = ".." }
# ///
from __future__ import annotations

import argparse
import sys
import time
from collections import Counter
from pathlib import Path

from smooth import SmoothClient

from eval.judge import exact_match, llm_judge
from eval.model import EvaluationResult, Task, load_tasks

TASK_PROMPT = """Go to {web_url} ({web_title}) and complete the following task:
{task}

Provide ONLY the final answer with no extra explanation."""


def run_task(
    task: Task,
    client: SmoothClient,
    *,
    max_steps: int,
    agent: str,
    stealth_mode: bool,
):
    prompt = TASK_PROMPT.format(
        web_url=task.web_url, web_title=task.web_title, task=task.task
    )
    start = time.monotonic()
    result = client.run(
        task=prompt,
        url=task.web_url,
        max_steps=max_steps,
        agent=agent,
        stealth_mode=stealth_mode,
    )
    duration = time.monotonic() - start
    return result, duration


def judge_task(
    task: Task,
    agent_name: str,
    model: str,
    answer: str,
    *,
    steps: int,
    duration_seconds: float,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
) -> EvaluationResult:
    kwargs = dict(
        steps=steps,
        duration_seconds=duration_seconds,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )
    if task.answer_type == "llm_judge":
        return llm_judge(task, agent_name, model, answer, **kwargs)
    return exact_match(task, agent_name, model, answer, **kwargs)


def print_summary(results: list[EvaluationResult], tasks: list[Task]) -> None:
    task_map = {t.id: t for t in tasks}
    total = len(results)
    correct = sum(r.is_correct for r in results)

    print("\n" + "=" * 60)
    print(f"Results: {correct}/{total} ({correct / total * 100:.1f}%)")
    print("=" * 60)

    # Breakdown by level
    level_total: Counter[str] = Counter()
    level_correct: Counter[str] = Counter()
    for r in results:
        t = task_map[r.task_id]
        level_total[t.level] += 1
        if r.is_correct:
            level_correct[t.level] += 1

    print("\nBy difficulty:")
    for level in ("easy", "medium", "hard"):
        t, c = level_total[level], level_correct[level]
        if t:
            print(f"  {level:8s}: {c}/{t} ({c / t * 100:.1f}%)")

    # Breakdown by task type
    type_total: Counter[str] = Counter()
    type_correct: Counter[str] = Counter()
    for r in results:
        t = task_map[r.task_id]
        type_total[t.task_type] += 1
        if r.is_correct:
            type_correct[t.task_type] += 1

    print("\nBy task type:")
    for task_type in ("lookup", "filter", "compare", "compute", "multi-step"):
        t, c = type_total[task_type], type_correct[task_type]
        if t:
            print(f"  {task_type:12s}: {c}/{t} ({c / t * 100:.1f}%)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate smooth agent")
    parser.add_argument(
        "--model",
        default="smooth",
        choices=["smooth", "smooth-lite"],
        help="Smooth agent variant",
    )
    parser.add_argument(
        "--tasks-file", default="tasks.jsonl", help="Path to tasks JSONL"
    )
    parser.add_argument(
        "--output", default="results/smooth.jsonl", help="Output JSONL path"
    )
    parser.add_argument(
        "--max-steps", type=int, default=32, help="Max agent steps per task (2-128)"
    )
    parser.add_argument(
        "--stealth-mode", action=argparse.BooleanOptionalAction, default=False
    )
    parser.add_argument(
        "--task-id", action="append", help="Filter to specific task IDs"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tasks = load_tasks(args.tasks_file)

    if args.task_id:
        task_ids = set(args.task_id)
        tasks = [t for t in tasks if t.id in task_ids]
        if not tasks:
            print(f"No tasks matched: {args.task_id}", file=sys.stderr)
            sys.exit(1)

    client = SmoothClient()
    agent_name = "smooth"

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results: list[EvaluationResult] = []

    with open(output_path, "w") as f:
        for i, task in enumerate(tasks, 1):
            print(f"\n[{i}/{len(tasks)}] {task.id}: {task.task[:80]}")

            try:
                smooth_result, duration_seconds = run_task(
                    task,
                    client,
                    max_steps=args.max_steps,
                    agent=args.model,
                    stealth_mode=args.stealth_mode,
                )
                print(f"  Live: {smooth_result.live_url()}")
                task_result = smooth_result.result()
                answer = task_result.output if task_result else ""
                if not isinstance(answer, str):
                    answer = str(answer)
                error = None
            except Exception as e:
                print(f"  ERROR: {e}")
                answer = ""
                duration_seconds = 0.0
                error = str(e)

            if error:
                result = EvaluationResult(
                    task_id=task.id,
                    agent=agent_name,
                    model=args.model,
                    answer=answer,
                    is_correct=False,
                    reason=None,
                    error=error,
                    steps=0,
                    duration_seconds=duration_seconds,
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                )
            else:
                result = judge_task(
                    task,
                    agent_name,
                    args.model,
                    answer,
                    steps=0,
                    duration_seconds=duration_seconds,
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                )
            results.append(result)

            f.write(result.model_dump_json() + "\n")
            f.flush()

            correct_so_far = sum(r.is_correct for r in results)
            status = "CORRECT" if result.is_correct else "WRONG"
            print(f"  Answer: {answer[:120]}")
            print(f"  {status} (running: {correct_so_far}/{i})")

    print_summary(results, tasks)


if __name__ == "__main__":
    main()

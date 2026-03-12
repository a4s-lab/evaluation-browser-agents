# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "eval",
# ]
# [tool.uv.sources]
# eval = { path = ".." }
# ///
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from eval.judge import llm_judge
from eval.model import EvaluationResult, Task, load_tasks

TASK_PROMPT = """Go to {web_url} ({web_title}) and complete the following task:
{task}

Provide ONLY the final answer with no extra explanation."""


@dataclass
class A4sResult:
    steps: int
    tokens: int
    task_completed: bool
    summary: str
    output: str | None


def parse_a4s_output(stdout: str) -> A4sResult:
    """Parse the structured output from the a4s simulator CLI."""
    lines = stdout.split("\n")
    result = A4sResult(steps=0, tokens=0, task_completed=False, summary="", output=None)

    in_result = False
    for line in lines:
        if "--- Agent Result ---" in line:
            in_result = True
            continue
        if not in_result:
            continue

        if line.startswith("steps:"):
            result.steps = int(line.split(":", 1)[1].strip())
        elif line.startswith("tokens:"):
            result.tokens = int(line.split(":", 1)[1].strip())
        elif line.startswith("task_completed:"):
            result.task_completed = line.split(":", 1)[1].strip() == "true"
        elif line.startswith("output:"):
            result.output = line.split(":", 1)[1].strip()
        elif line.startswith("summary:"):
            result.summary = line.split(":", 1)[1].strip()

    return result


def run_task(
    task: Task,
    binary: str,
    *,
    model: str,
    provider: str,
    lite_model: str | None,
    max_steps: int,
    headless: bool,
) -> tuple[A4sResult, float]:
    prompt = TASK_PROMPT.format(
        web_url=task.web_url, web_title=task.web_title, task=task.task
    )
    cmd = [
        binary,
        "run",
        "--env",
        "browser",
        "--url",
        task.web_url,
        "--max-steps",
        str(max_steps),
        "--model",
        model,
    ]
    if headless:
        cmd.append("--headless")
    cmd.append(prompt)

    env = {
        **os.environ,
        "LLM_API_KEY": os.environ.get(
            "LLM_API_KEY", os.environ.get("OPENAI_API_KEY", "")
        ),
        "LLM_PROVIDER": provider,
    }
    if lite_model:
        env["LITE_LLM_MODEL"] = lite_model

    start = time.monotonic()
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, env=env)
    duration = time.monotonic() - start

    if proc.returncode != 0:
        raise RuntimeError(
            f"simulator exited with code {proc.returncode}: {proc.stderr.strip()}"
        )

    return parse_a4s_output(proc.stdout), duration


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
    return llm_judge(task, agent_name, model, answer, **kwargs)


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
    parser = argparse.ArgumentParser(description="Evaluate a4s simulator agent")
    parser.add_argument(
        "--binary", required=True, help="Path to built simulator binary"
    )
    parser.add_argument("--model", default="gpt-4o", help="LLM model name")
    parser.add_argument(
        "--provider", default="openai", help="LLM provider (openai, openrouter)"
    )
    parser.add_argument("--lite-model", help="Lite LLM model name")
    parser.add_argument(
        "--tasks-file", default="tasks.jsonl", help="Path to tasks JSONL"
    )
    parser.add_argument("--output-dir", default="results", help="Output directory")
    parser.add_argument(
        "--max-steps", type=int, default=64, help="Max agent steps per task"
    )
    parser.add_argument(
        "--headless", action=argparse.BooleanOptionalAction, default=True
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

    agent_name = "a4s"

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"a4s-{int(time.time())}.jsonl"

    results: list[EvaluationResult] = []

    with open(output_path, "w") as f:
        for i, task in enumerate(tasks, 1):
            print(f"\n[{i}/{len(tasks)}] {task.id}: {task.task[:80]}")

            try:
                a4s_result, duration_seconds = run_task(
                    task,
                    args.binary,
                    model=args.model,
                    provider=args.provider,
                    lite_model=args.lite_model,
                    max_steps=args.max_steps,
                    headless=args.headless,
                )
                answer = a4s_result.output or a4s_result.summary
                steps = a4s_result.steps
                total_tokens = a4s_result.tokens
                error = None
            except Exception as e:
                print(f"  ERROR: {e}")
                answer = ""
                steps = 0
                total_tokens = 0
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
                    steps=steps,
                    duration_seconds=duration_seconds,
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=total_tokens,
                )
            else:
                result = judge_task(
                    task,
                    agent_name,
                    args.model,
                    answer,
                    steps=steps,
                    duration_seconds=duration_seconds,
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=total_tokens,
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

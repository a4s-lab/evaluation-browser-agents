import os

from openai import OpenAI

from eval.model import EvaluationResult, Task

JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "gpt-4o")

# Inspired by WebVoyager's auto_eval.py
JUDGE_SYSTEM_PROMPT = """As an evaluator, you will be presented with three primary components to assist you in your role:

1. Web Task Instruction: This is a clear and specific directive provided in natural language, detailing the online activity to be carried out. These requirements may include conducting searches, verifying information, comparing prices, checking availability, or any other action relevant to the specified web service (such as Amazon, Apple, ArXiv, BBC News, Booking etc).

2. Reference Answer: This is the ground-truth answer for the task, which serves as the benchmark for evaluating the result response.

3. Result Response: This is a textual response obtained after the execution of the web task. It serves as textual result in response to the instruction.

-- You DO NOT NEED to interact with web pages or perform actions.
-- Your primary responsibility is to conduct a thorough assessment of the web task instruction against the result response and reference answer, evaluating whether the actions taken align with the given instructions.
-- NOTE that the instruction may involve more than one task. Failing to complete any sub-task should be considered unsuccessful.

You should elaborate on how you arrived at your final evaluation and then provide a definitive verdict on whether the task has been successfully accomplished, either as 'SUCCESS' or 'NOT SUCCESS'."""

JUDGE_USER_PROMPT = """TASK: {task}
Reference Answer: {reference}
Result Response: {predicted}"""


def llm_judge(
    task: Task,
    agent: str,
    model: str,
    predicted: str,
    *,
    steps: int,
    duration_seconds: float,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
) -> EvaluationResult:
    """Use an LLM to judge whether the predicted answer is correct."""
    client = OpenAI()
    user_prompt = JUDGE_USER_PROMPT.format(
        task=task.task,
        reference=task.answer,
        predicted=predicted,
    )
    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1000,
        temperature=0,
        seed=42,
    )
    content = response.choices[0].message.content or ""
    is_correct = "NOT SUCCESS" not in content and "SUCCESS" in content
    return EvaluationResult(
        task_id=task.id,
        agent=agent,
        model=model,
        answer=predicted,
        is_correct=is_correct,
        reason=content,
        steps=steps,
        duration_seconds=duration_seconds,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )

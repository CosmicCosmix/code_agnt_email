import asyncio
import os
import json
from openai import OpenAI
from env import EmailTriageEnv, VALID_FOLDERS
from models import TriageAction
from tasks import grade_easy_task, grade_medium_task, grade_hard_task

# ---------------------------------------------------------------------------
# CONFIGURATION — all credentials come from environment variables
# ---------------------------------------------------------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "dummy-key")

# ---------------------------------------------------------------------------
# MANDATORY LOG FORMAT  (do not alter — judges parse these lines)
# ---------------------------------------------------------------------------
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error) -> None:
    error_val = error if error else "null"
    done_val  = str(done).lower()
    print(
        f"[STEP] step={step} action={action} "
        f"reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float, rewards: list) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} "
        f"score={score:.3f} rewards={rewards_str}",
        flush=True,
    )

# ---------------------------------------------------------------------------
# SYSTEM PROMPT — tells the AI what it can and cannot do
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = f"""
You are an email triage assistant. Your job is to read emails from an inbox
and move each one to the correct folder.

VALID FOLDERS (use these exact strings, nothing else):
{json.dumps(sorted(VALID_FOLDERS), indent=2)}

Folder guide:
- Personal       : Appointments, social messages, personal newsletters, bank
                   statements unrelated to work, promotional emails.
- Billing        : Invoices and receipts from cloud/SaaS providers
                   (AWS, Azure, GCP, GitHub, Vercel, etc.).
- Feedback/Suggestion : Customer emails that propose a new feature or improvement.
- Feedback/Complaint  : Customer emails expressing anger, reporting a problem,
                        or demanding a fix.
- Feedback/Query      : Customer emails asking a question or requesting information.
- HR             : Internal company emails about training, appraisals, policies.

IMPORTANT:
- Billing emails come from official corporate domains
  (e.g. @aws.amazon.com, @microsoft.com, @google.com).
- Personal AND customer feedback emails often come from civilian addresses
  (gmail, yahoo, outlook, etc.). Read the body to tell them apart.
- Respond ONLY with a JSON object with two keys:
    "email_id"      (integer)
    "target_folder" (string — must be one of the valid folders above)
- Do not add any explanation, preamble, or markdown.
""".strip()

# ---------------------------------------------------------------------------
# RUN ONE TASK EPISODE
# ---------------------------------------------------------------------------
async def run_task(task_name: str, grader, client: OpenAI) -> float:
    env = EmailTriageEnv()
    obs = env.reset()

    log_start(task=task_name, env="email_triage", model=MODEL_NAME)

    rewards      = []
    steps_taken  = 0
    conversation = []   # Rolling message history for multi-turn context

    for step in range(1, env.max_steps + 1):
        steps_taken = step

        # Build the user message for this step
        user_content = (
            f"Current inbox ({obs.inbox_count} emails remaining):\n"
            f"{obs.model_dump_json(indent=2)}\n\n"
            f"Pick one email to move. Reply with JSON only."
        )
        conversation.append({"role": "user", "content": user_content})

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation,
                max_tokens=100,
                temperature=0.2,   # Low temperature = more deterministic triage
            )

            raw_reply = response.choices[0].message.content.strip()
            conversation.append({"role": "assistant", "content": raw_reply})

            # Strip markdown fences if model wraps JSON in them
            clean = raw_reply.strip("`").strip()
            if clean.startswith("json"):
                clean = clean[4:].strip()

            action_data = json.loads(clean)
            action      = TriageAction(**action_data)

            obs, reward, done, info = env.step(action)
            rewards.append(reward)

            log_step(step, str(action.model_dump()), reward, done, None)

            if done:
                break

        except Exception as e:
            log_step(step, "error", 0.0, True, str(e))
            break

    # Final grader score (0.0 – 1.0)
    final_score = grader(env)
    success     = final_score >= 0.5

    log_end(success, steps_taken, final_score, rewards)
    return final_score


# ---------------------------------------------------------------------------
# MAIN — runs all 3 tasks sequentially
# ---------------------------------------------------------------------------
async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    tasks = [
        ("easy_personal",    grade_easy_task),
        ("medium_billing_hr", grade_medium_task),
        ("hard_feedback",    grade_hard_task),
    ]

    all_scores = []
    for task_name, grader in tasks:
        score = await run_task(task_name, grader, client)
        all_scores.append(score)
        print(f"\n>>> Task '{task_name}' final grader score: {score:.3f}\n", flush=True)

    overall = sum(all_scores) / len(all_scores)
    print(f"=== OVERALL SCORE: {overall:.3f} ===", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
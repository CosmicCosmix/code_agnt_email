import asyncio
import os
import json
from openai import OpenAI
from env import EmailTriageEnv, VALID_FOLDERS
from models import TriageAction
from tasks import grade_easy_task, grade_medium_task, grade_hard_task

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "dummy-key")

MAX_STEPS             = 25
SUCCESS_SCORE_THRESHOLD = 0.5

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

SYSTEM_PROMPT = f"""
You are an email triage assistant. Your job is to read emails from an inbox
and move each one to the correct folder.

VALID FOLDERS (use these exact strings, nothing else):
{json.dumps(sorted(f for f in VALID_FOLDERS if f != "inbox"), indent=2)}

Folder guide:
- Personal              : Appointments, social messages, newsletters, promotions,
                          personal bank statements.
- Billing               : Invoices and receipts from cloud/SaaS providers
                          (AWS, Azure, GCP, GitHub, Vercel, etc.).
- Feedback/Suggestion   : Customer emails proposing a new feature or improvement.
- Feedback/Complaint    : Customer emails reporting a problem, expressing frustration,
                          or demanding a fix.
- Feedback/Query        : Customer emails asking a question or requesting information.
- HR                    : Internal company emails about training, appraisals, policies.

IMPORTANT:
- Billing emails come from official corporate domains (@aws.amazon.com, @microsoft.com, etc.).
- Personal AND Feedback emails often share civilian addresses (gmail, yahoo, outlook).
  Read the body carefully to tell them apart.
- Respond ONLY with a JSON object with exactly two keys:
    "email_id"      (integer)
    "target_folder" (string — must be one of the valid folders above)
- No explanation, no preamble, no markdown fences.
""".strip()

async def run_task(task_name: str, grader, client: OpenAI) -> float:
    env          = EmailTriageEnv()
    obs          = env.reset()
    rewards      = []
    steps_taken  = 0
    conversation = []

    log_start(task=task_name, env="email_triage", model=MODEL_NAME)

    try:
        for step in range(1, MAX_STEPS + 1):
            steps_taken = step

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
                    temperature=0.2,
                )

                raw_reply = response.choices[0].message.content.strip()
                conversation.append({"role": "assistant", "content": raw_reply})

                # Strip markdown fences if the model adds them
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

    finally:
       
        final_score = grader(env)
        success     = final_score >= SUCCESS_SCORE_THRESHOLD
        log_end(success, steps_taken, final_score, rewards)

    return final_score

async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    tasks = [
        ("easy_personal",     grade_easy_task),
        ("medium_billing_hr", grade_medium_task),
        ("hard_feedback",     grade_hard_task),
    ]

    all_scores = []
    for task_name, grader in tasks:
        score = await run_task(task_name, grader, client)
        all_scores.append(score)
        print(f"\n>>> Task '{task_name}' grader score: {score:.4f}\n", flush=True)

    overall = sum(all_scores) / len(all_scores)
    print(f"=== OVERALL SCORE: {overall:.3f} ===", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
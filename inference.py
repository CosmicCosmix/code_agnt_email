import asyncio
import os
import json
from openai import OpenAI
from env import EmailTriageEnv
from models import TriageAction

API_BASE_URL = os.getenv("API_BASE_URL", "<your-active-endpoint>")
MODEL_NAME = os.getenv("MODEL_NAME", "<your-active-model>")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "dummy-key")

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: str) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: list) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = EmailTriageEnv() # Initialize your backend
    
    log_start(task="email_triage", env="openenv", model=MODEL_NAME)
    
    rewards = []
    steps_taken = 0
    success = False
    
    # 1. Reset the environment (Get initial observation)
    obs = env.reset()
    
    for step in range(1, 6): # Max 5 steps
        steps_taken = step
        
        # 2. Ask the LLM what to do
        prompt = f"Inbox state: {obs.model_dump_json()}. Reply ONLY with JSON containing 'email_id' (int) and 'target_folder' (str)."
        
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 3. Parse LLM response into our Action Model
            action_data = json.loads(response.choices[0].message.content)
            action = TriageAction(**action_data)
            
            # 4. Step the environment
            obs, reward, done, info = env.step(action)
            rewards.append(reward)
            
            log_step(step, str(action.model_dump()), reward, done, None)
            
            if done:
                break
                
        except Exception as e:
            log_step(step, "error", 0.0, True, str(e))
            break

    # Calculate final score (simplified for example)
    score = sum(rewards) / 3.0
    score = min(max(score, 0.0), 1.0)
    success = score > 0.5
    
    log_end(success, steps_taken, score, rewards)

if __name__ == "__main__":
    asyncio.run(main())
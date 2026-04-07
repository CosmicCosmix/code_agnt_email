from fastapi import FastAPI
from pydantic import BaseModel
from env import EmailTriageEnv
from models import TriageAction
app = FastAPI()
env = EmailTriageEnv()
@app.post("/reset")
def reset():
    obs = env.reset()
    return obs.model_dump()
@app.post("/step")
def step(action: TriageAction):
    obs, reward, done, info = env.step(action)
    return {"observation": obs.model_dump(), "reward": reward, "done": done, "info": info}
@app.get("/state")
def state():
    return env.state()
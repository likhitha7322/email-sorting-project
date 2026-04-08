from fastapi import FastAPI
from pydantic import BaseModel
from env import EmailSortingEnv

app = FastAPI()

env = EmailSortingEnv()


class ActionInput(BaseModel):
    label: str
    confidence: float = 1.0


@app.post("/reset")
def reset():
    obs = env.reset()
    return obs.__dict__


@app.post("/step")
def step(action: ActionInput):
    from models import Action

    act = Action(label=action.label, confidence=action.confidence)
    obs, reward, done, info = env.step(act)

    return {
        "observation": None if obs is None else obs.__dict__,
        "reward": reward.score,
        "done": done,
        "info": info
    }

import os
from flask import Flask, request, jsonify
from env import EmailSortingEnv
from Agents import get_agent
from models import Observation

app = Flask(__name__)

agent = get_agent("EnsembleAgent")
env = EmailSortingEnv()

@app.route("/reset", methods=["POST"])
def reset():
    data = request.json or {}
    difficulty = data.get("difficulty")
    noise = data.get("noise")
    obs = env.reset(difficulty=difficulty, noise=noise)
    return jsonify(obs.dict())

@app.route("/step", methods=["POST"])
def step():
    obs_data = request.json
    obs = Observation(**obs_data)
    action = agent.predict(obs)
    return jsonify(action.dict())

@app.route("/state", methods=["GET"])
def state():
    return jsonify(env.state())

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "agent": agent.name})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port)

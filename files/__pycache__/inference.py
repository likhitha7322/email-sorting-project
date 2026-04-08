import os
from env import EmailSortingEnv
from Agents import ALL_AGENTS, get_agent
# REQUIRED ENV VARIABLES
API_BASE_URL = os.getenv("API_BASE_URL", "")
MODEL_NAME = os.getenv("MODEL_NAME", "")

def main():
    agent = get_agent("baseline")  # or your agent name

    env = EmailSortingEnv()
    obs = env.reset()

    results = []

    while obs is not None:
        action = agent.predict(obs)
        obs, reward, done, info = env.step(action)

        results.append({
            "label": action.label,
            "score": reward.score
        })

    print(results)


if __name__ == "__main__":
    main()

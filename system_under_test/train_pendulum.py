from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
import gymnasium as gym
import numpy as np

# Create the environment
env_id = "Pendulum-v1"
env = make_vec_env(env_id, n_envs=1)

# Instantiate the agent
model = PPO(
    "MlpPolicy",
    env,
    gamma=0.98,
    use_sde=True,
    sde_sample_freq=4,
    learning_rate=1e-3,
    verbose=1
)

# Train the agent
model.learn(total_timesteps=int(3.5e4))
model.save("./system_under_test/pendulum_ppo")


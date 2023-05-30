from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
import gymnasium as gym
import numpy as np

# Create the environment
# env_id = "Pendulum-v1"
# env = make_vec_env(env_id, n_envs=1)

# # Instantiate the agent
# model = PPO(
#     "MlpPolicy",
#     env,
#     gamma=0.98,
#     use_sde=True,
#     sde_sample_freq=4,
#     learning_rate=1e-3,
#     verbose=1,
# )

# # Train the agent
# model.learn(total_timesteps=int(1e5))
# model.save("./system_under_test/pendulum_ppo")

# del model
env = gym.make("Pendulum-v1")

model = PPO.load("./system_under_test/pendulum_ppo")
obs = env.reset()[0]
terminated = False
truncated = False
counter = 0
while np.logical_and(np.logical_not(terminated),np.logical_not(truncated)):
    counter += 1
    action, _states = model.predict(obs)
    obs, rewards, terminated, truncated, infor = env.step(action)
    print(counter, terminated,truncated)
    # env.render()



print("stop")
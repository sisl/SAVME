import numpy as np
from system_under_test.pendulum_physics import PendulumEnv
from stable_baselines3 import PPO


BINS_X = 100
BINS_Y = 100
BINS_VEL = 100
FREQ = 20
DT = 1/FREQ
DURATION = 10   #in sec
REQ_STEPS = FREQ * DURATION

env = PendulumEnv()
env.dt = DT
env.max_steps = REQ_STEPS

model = PPO.load("./system_under_test/pendulum_ppo")
obs = env.reset(options={"init":np.array([0.67,-0.2])})[0]
print(np.arctan2(obs[1],obs[0]),obs[2])
terminated = False
truncated = False
counter = 0

while np.logical_and(np.logical_not(terminated),np.logical_not(truncated)):
    # print(counter)
    counter += 1
    action, _states = model.predict(obs,deterministic=True)
    print(action,obs)
    obs, rewards, terminated, truncated, infor = env.step(action)
    digitized_obs = np.zeros_like(obs)
    #digitize observations
    obs_x_bin_boundaries = np.linspace(-1,1,BINS_X+1)
    obs_x_bin_values = (obs_x_bin_boundaries[:-1] + obs_x_bin_boundaries[1:]) / 2
    obs_x_idx = np.clip(np.digitize(obs[0],obs_x_bin_boundaries),1,BINS_X) - 1
    obs_x = obs_x_bin_values[obs_x_idx]
    digitized_obs[0] = obs_x

    obs_y_bin_boundaries = np.linspace(-1,1,BINS_Y+1)
    obs_y_bin_values = (obs_y_bin_boundaries[:-1] + obs_y_bin_boundaries[1:]) / 2
    obs_y_idx = np.clip(np.digitize(obs[1],obs_y_bin_boundaries),1,BINS_Y) - 1
    obs_y = obs_y_bin_values[obs_y_idx]
    digitized_obs[1] = obs_y

    obs_vel_bin_boundaries = np.linspace(-8,8,BINS_VEL+1)
    obs_vel_bin_values = (obs_vel_bin_boundaries[:-1] + obs_vel_bin_boundaries[1:]) / 2
    obs_vel_idx = np.clip(np.digitize(obs[2],obs_vel_bin_boundaries),1,BINS_VEL) - 1
    obs_vel = obs_vel_bin_values[obs_vel_idx]
    digitized_obs[2] = obs_vel

#get final angle theta
theta = np.arctan2(obs[1],obs[0])
allowable_deviation = 5 #in deg
if np.abs(theta*180/np.pi)>=allowable_deviation:
    failure = True
else:
    failure = False
print(theta*180/np.pi)
print(failure)


print("stop")
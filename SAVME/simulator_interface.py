import random
import string
import os
import pickle
import numpy as np
import torch
import time
from system_under_test.pendulum_physics import PendulumEnv
from stable_baselines3 import PPO
from datetime import datetime


def run_hf_lf(scenario,scenario_config,HF_config,LF_config):
    """This function runs a parallel simulation using the high and learned-fidelity simulators
    Parameters:
    -----------
    scenario: scenario to simulate
    scenario_config (dict): dictionary of all the scenario configuration keys and values
    HF_config (dict): dictionary of all the high fidelity setting keys and their values
    LF_config (dict): dictionary of all the learned fidelity setting keys and their values

    Returns:
    --------
    cost_ratio (float): The ratio of cost_lf/cost_hf (t_LF/t_HF), that is the ratio of running the low-fidelity simulation compared to the high fidelity simulation
    outcome_type (str): Can either be "TP" indicating that both the the HF and LF found a failure of the system, "TN", that both systems agreed that there was no failure, "FP" meaning that the low-fidelity simulator predicted a failure while the high-fidelity simulator doesn't predict a failure, or "FN" when the low-fidelity simulator doesn't predict a failure, but the high-fidelity simulator predicts a failure.
    name (str): Unique identifier for the run which is used to identify the log files or other possible files associated with the run
    """

    now = datetime.now()
    name = now.strftime("%Y%m%d%H%M%S%f")


    #####################################################################
    #######################HIGH-FIDELITY#################################
    #####################################################################
    start_HF = time.time()
    BINS_X = HF_config["BINS_X"]
    BINS_Y = HF_config["BINS_Y"]
    BINS_VEL = HF_config["BINS_VEL"]
    FREQ = HF_config["FREQ"]
    
    DT = 1/FREQ
    DURATION = 10   #in sec
    REQ_STEPS = int(FREQ * DURATION)

    env = PendulumEnv()
    env.dt = DT
    env.max_steps = REQ_STEPS

    model = PPO.load("./system_under_test/pendulum_ppo") 

    obs = env.reset(options={"init":np.array([scenario_config["THETA_INIT"],scenario_config["THETA_DOT_INIT"]])})[0]
    digitized_obs = obs
    # print(np.arctan2(obs[1],obs[0]),obs[2])
    terminated = False
    truncated = False
    counter = 0

    while np.logical_and(np.logical_not(terminated),np.logical_not(truncated)):
        # print(counter)
        counter += 1
        action, _states = model.predict(digitized_obs,deterministic=True) #deterministic=True necessary to avoid sampling from policy. We want the a deterministic system under test here for simplicity (although in theory this is not required).
        obs, rewards, terminated, truncated, info = env.step(action) 
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
    if np.abs(theta*180/np.pi)>=allowable_deviation:    #if the final absolute value of the angle theta is more than 10 deg, we conclude that we found a failure of the system as the pendulum is not in the desired final position
        failure_HF = True
    else:
        failure_HF = False
    
    time_HF = time.time() - start_HF

    #####################################################################
    #######################LEARNED-FIDELITY#################################
    #####################################################################
    start_LF = time.time()

    BINS_X = LF_config["BINS_X"]
    BINS_Y = LF_config["BINS_Y"]
    BINS_VEL = LF_config["BINS_VEL"]
    FREQ = LF_config["FREQ"]
    
    DT = 1/FREQ
    DURATION = 10   #in sec
    REQ_STEPS = FREQ * DURATION

    env = PendulumEnv()
    env.dt = DT
    env.max_steps = REQ_STEPS

    model = PPO.load("./system_under_test/pendulum_ppo")
    obs = env.reset(options={"init":np.array([scenario_config["THETA_INIT"],scenario_config["THETA_DOT_INIT"]])})[0]
    digitized_obs = obs
    terminated = False
    truncated = False
    counter = 0

    while np.logical_and(np.logical_not(terminated),np.logical_not(truncated)):
        # print(counter)
        counter += 1
        action, _states = model.predict(digitized_obs,deterministic=True) #deterministic=True necessary to avoid sampling from policy. We want the a deterministic system under test here for simplicity (although in theory this is not required).
        obs, rewards, terminated, truncated, info = env.step(action)
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
        failure_LF = True
    else:
        failure_LF = False

    time_LF = time.time() - start_LF

    #outcome type
    if (failure_HF==True) and (failure_LF==True):
        outcome_type = "TP"
    elif (failure_HF==True) and (failure_LF==False):
        outcome_type = "FN"
    elif (failure_HF==False) and (failure_LF==True):
        outcome_type = "FP"
    elif (failure_HF==False) and (failure_LF==False):
        outcome_type = "TN"
    else:
        raise NotImplementedError("Unspported datatype for 'failure_HF' or 'failure_LF'. Only boolean values are supported." )

    #cost ratio
    cost_ratio = time_LF/time_HF
    
    return cost_ratio, outcome_type, name, time_HF, time_LF


import random
import string
import os
import pickle
import numpy as np
import torch
import time

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
    cost_ratio = 0.5
    outcome_type = "TP"
    name = "demo_example"
    
    return cost_ratio, outcome_type, name

if __name__ == "__main__":
    import gymnasium as gym

    env = gym.make("Pendulum-v1",render_mode="rgb_array")
    obs, info = env.reset()
    for _ in range(200):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        env.render()
        time.sleep(0.1)
    
    env.close()
    print("stop")

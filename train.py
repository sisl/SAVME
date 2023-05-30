import pickle

from SAVME.settings import Settings
from SAVME.meta_env import MetaEnv
from SAVME.simulator_interface import run_hf_lf

from scenarios.training_scenario import TrainingScenario
from scenarios.testing_scenario import TestingScenario


######################################################################
###########################SETUP######################################
######################################################################

scenarios = {"traing_scenario": TrainingScenario()}    #We use and object for each scenario that contains all the nececssary logistics and can be expanded as necessary. We only use the "get_constraints" method here to obtain the scenario parameters and their constraints.

scenarios_meta_test = {"testing_scenario": TestingScenario()}   #The same applies here as for the "scenarios"
    
scenarios_with_config = {name:{"scenario":scenarios[name],"settings":Settings(scenarios[name].get_constraints()),"weight":1/len(scenarios)} for name in scenarios.keys()}   #We use the "get_constraints" method from the scenarios to obtain the scenario specific parameters and their constraints

scenarios_meta_test_with_config = {name:{"scenario":scenarios_meta_test[name],"settings":Settings(scenarios_meta_test[name].get_constraints()),"weight":1/len(scenarios_meta_test)} for name in scenarios_meta_test.keys()} #The "get_constraints" method is used to obtain the scenario specific parameters and their constraints

#similarly to scenario parameters, we also need to define the fidelity settings. The names of the fidelity settings must be recognized by the "run_hf_lf" function that carries out the simulation
#Our demo problem is the inverted pendulum from Gymnasium (previously: OpenAI Gym). This problem has three observations: the x-position of the tip of the pendulum, the y-position of the tip of the pendulum and the angualar velocity. 
#To mimic the simulation fidelity, we discretize each of the outputs and only pass the discretized values to the system under test. The higher the number of bins, the closer the value is to the continuous signal.
#Finally, we also have control over the simulation frequency (in Hz). The simulated time is always 10s and the number of simulation steps is determined based on the frequency
fidelity_settings_config = {"BINS_X":{"var_type":"discrete","values":(1,2,5,10,20,50,100)}, #number of bins for the rod tip x-position
                            "BINS_Y":{"var_type":"discrete","values":(1,2,5,10,20,50,100)}, #number of bins for the rod tip y-position
                            "BINS_VEL":{"var_type":"discrete","values":(1,2,5,10,20,50,100)}, #number of bins for the angular velocity of the rod
                            "FREQ":{"var_type":"continuous","values":(1.,100.),"bins":10,"bin_edge_type":"log"}} #simulation frequency. We use the logarithmic ("log") bin_edge_type which spaces the bins logarithmically apart.

fidelity_settings = Settings(fidelity_settings_config)  #convert the fidelity settings into a Settings object. We use setting objects to keep track of the distributions over the fidelity settings and to extract the MAP estimate for the evaluation phase

#The high-fidelity settings themselves must have the same keys as the "fidelity_settings_config" dictionarty and the values specified must be with in the set of specified values for discrete variables or within the range for continuous variables
high_fidelity_settings = {"BINS_X":100,
                          "BINS_Y":100,
                          "BINS_VEL":100,
                          "FREQ":100.}


######################################################################
###########################EXPERIMENTS################################
######################################################################
meta_env = MetaEnv(scenarios_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.1)
meta_env.mc(1000,"mc_test")
# print("stop")

###########################META-TRAINING##############################
meta_env = MetaEnv(scenarios_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.1) #The MetaEnv object handles all the training, evaluation, and testing. We need to pass it the scenarios alongside with their configurations, the high-fidelity settings, the fidelity setting configurations (for the learned-fidelity settings), the run_hf_lf functions and the compute budget. The compute budget is the target fraction of time_LF and time_HF. For more details, see the paper.
meta_env.train(1000,"train_0_1")
meta_env.eval(100,"eval_0_1")
print("stop")

# # meta_env = MetaEnv(scenarios_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.4)
# # meta_env.train(500,"007_C")
# # meta_env.eval(100,"008_C")

# # meta_env = MetaEnv(scenarios_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.3)
# # meta_env.train(500,"010_C")
# # meta_env.eval(100,"011_C")

# meta_env = MetaEnv(scenarios_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.2)
# meta_env.train(500,"012_C")
# meta_env.eval(100,"013_C")

# ####################NEW META-TESTING################################################
# #######020########
# #starting from scratch
# meta_env_no_prior = MetaEnv(scenarios_meta_test_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.3)
# meta_env_no_prior.train(200,"020_C_no_prior_train")
# # meta_env_no_prior = load_from_file("./results/020_B_no_prior_train.pkl",run_hf_lf,compute_budget=0.3)
# # meta_env_no_prior.train_iter = 0
# # meta_env_no_prior.history = []
# meta_env_no_prior.eval(100,"020_C_no_prior_eval")

# #starting with prior
# with open("./results/010_C.pkl","rb") as f:   #010 is the training with budget 0.3
#     data = pickle.load(f)

# extracted_fidelity_settings = data[-1]["fidelity_settings_state"]
# meta_env_w_prior = MetaEnv(scenarios_meta_test_with_config,high_fidelity_settings,extracted_fidelity_settings,run_hf_lf,compute_budget=0.3)
# meta_env_w_prior.train(200,"020_C_w_prior_train")
# meta_env_w_prior.eval(100,"020_C_w_prior_eval")

# #######021########
# #starting from scratch
# meta_env_no_prior = MetaEnv(scenarios_meta_test_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.4)
# meta_env_no_prior.train(200,"021_C_no_prior_train")
# meta_env_no_prior.eval(100,"021_C_no_prior_eval")

# #starting with prior
# with open("./results/007_C.pkl","rb") as f:   #007 is the training with budget 0.4
#     data = pickle.load(f)

# extracted_fidelity_settings = data[-1]["fidelity_settings_state"]
# meta_env_w_prior = MetaEnv(scenarios_meta_test_with_config,high_fidelity_settings,extracted_fidelity_settings,run_hf_lf,compute_budget=0.4)
# meta_env_w_prior.train(200,"021_C_w_prior_train")
# meta_env_w_prior.eval(100,"021_C_w_prior_eval")

# #######022########
# #starting from scratch
# meta_env_no_prior = MetaEnv(scenarios_meta_test_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.2)
# meta_env_no_prior.train(200,"022_C_no_prior_train")
# meta_env_no_prior.eval(100,"022_C_no_prior_eval")

# #starting with prior
# with open("./results/012_C.pkl","rb") as f:   #012 is the training with budget 0.2
#     data = pickle.load(f)

# extracted_fidelity_settings = data[-1]["fidelity_settings_state"]
# meta_env_w_prior = MetaEnv(scenarios_meta_test_with_config,high_fidelity_settings,extracted_fidelity_settings,run_hf_lf,compute_budget=0.2)
# meta_env_w_prior.train(200,"022_C_w_prior_train")
# meta_env_w_prior.eval(100,"022_C_w_prior_eval")

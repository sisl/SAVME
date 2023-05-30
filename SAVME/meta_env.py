import random
import pickle
from copy import copy
import numpy as np
import time
from tqdm import tqdm
from SAVME.settings import Settings

def load_from_file(filename,fun,compute_budget=None):   #function to load last state from file
    with open(filename,"rb") as f:
        history = pickle.load(f)
    
    # dummy_scenario_config = {"VAR0":{"var_type":"discrete","values":(1,2,3)},"VAR1": {"var_type":"continuous", "values":(163, 185)}}
    # dummy_scenarios = {"sc1":{"scenario":"a","scenario_settings":Settings(dummy_scenario_config),"weight":1}}
    scenario_settings = history[-1]["scenario_settings_state"]
    fidelity_settings = history[-1]["fidelity_settings_state"]
    hf_settings = history[-1]["hf_settings"]
    if compute_budget is None:
        c_budget = history[-1]["compute_budget"]
    else:
        c_budget = compute_budget
    
    meta_env = MetaEnv(scenario_settings,hf_settings,fidelity_settings,fun,c_budget)
    meta_env.train_iter = len(history)   #potentially need len(history) - 1
    meta_env.history = history

    return meta_env


class MetaEnv(object):
    def __init__(self,scenarios,hf_settings,fidelity_settings,run_hf_lf,compute_budget=1.0) -> None:
        self.scenarios = scenarios                          #dict of the structure {name:{"scenario":scenario,"settings":scenario_settings_config,"weight":weight},...} where name is the string that identifies the scenario, the scenario is any type of object that is used to pass to the run_hf_lf function, and scenario_settings_config is a Settings object for the scenario variables, weight is the weight with which the scenario is picked, if weights don't sum up to one, they will be normalized
        self.scenarios_keys = list(self.scenarios.keys())    #list of keys for all scenarios
        self.hf_settings = hf_settings                      #dict of high fidelity settings
        self.fidelity_settings = fidelity_settings          #Settings object
        self.compute_budget = compute_budget                #float that represents what the maximum compute budget is. Any simulation that returns a cost > self.compute budget will be considered a failure.
        self.run_hf_lf = run_hf_lf                          #function that is called to run the hf simulation and lf simulations. Arguments should be (scenario,scenario_settings,hf_settings,lf_settings) and returns (cost,return_type,runid)
        # self.run_hf = run_hf
        # self.run_lf = run_lf
        self.train_iter = 0                                 #initialize the iteration counter
        self.history = []
        self._normalize_weights()       

    def _normalize_weights(self):
        weights = np.array([self.scenarios[k]["weight"] for k in self.scenarios_keys])
        weights = weights/np.sum(weights)
        keys = list(self.scenarios_keys)
        for i in range(len(keys)):
            self.scenarios[keys[i]]["weight"] = weights[i]

    def train_one_step_hf_lf(self,filename="log"): #training to update the counts
        """
        1. randomly select one scenario 
        2. sample scenario_settings anf lf_settings via Thompson sampling
        3. run scenario using the self.run_hf_lf function
        4. Process the returns from self.run_hf_lf
            a. convert return_type ("TP","TN","FP","FN") and cost into success (return_type \in {"TP","TN"} \land cost<=self.compute_budget) or a failure
            b. update the scenario_settings and the lf_settings 
        5. Save all the results into a list of dictionaries {"iteration":self.train_iter,"runid":runid,"scenario":scenario_id,"cost":cost,"outcome_type":outcome_type,"scenario_config":scenario_config,"hf_config":hf_config,"lf_config":lf_config,"scenario_settings_state":copy(scenario_settings),"fidelity_settings_state":copy(fidelity_settings)}
        6. Print statistics
        7. Update self.train_iter
        """
        #step 1
        print("-"*80)
        scenario_key = random.choices(self.scenarios_keys,weights=[self.scenarios[k]["weight"] for k in self.scenarios_keys])[0]

        #step 2
        sampled_scenario_settings = self.scenarios[scenario_key]["settings"].sample_from_prior()
        sampled_lf_settings = self.fidelity_settings.sample_from_prior()

        #step 3
        cost, outcome_type, runid, t_HF, t_LF = self.run_hf_lf(self.scenarios[scenario_key]["scenario"],sampled_scenario_settings,self.hf_settings,sampled_lf_settings)

        #step 4a
        if np.logical_and(outcome_type in ["TP","TN"],cost<=self.compute_budget):
            #success for fidelity is if outcome_type in ["TP","TN"] and cost<=self.compute_budget
            binary_result_fidelity = 1
        elif np.logical_or(outcome_type in ["FP","FN"],cost>=self.compute_budget):
            binary_result_fidelity = 0
        else:
            raise ValueError("Returned outcome_type or cost are not of the expected value.")
        
        if outcome_type in ["TP","FN"]:
            #sucess for finding hard scenarios. In both "TP and "FN", the high-fidelity simulator found a failure is considered a success
            binary_result_scenario = 1
        elif outcome_type in ["TN","FP"]:
            binary_result_scenario = 0
        else:
            raise ValueError("outcome_type should be either 'TP', 'TN', 'FP', or 'FN'.")
        
        #step 4b
        #update scenario_settings
        self.scenarios[scenario_key]["settings"].update_prior(binary_result_scenario,sampled_scenario_settings)
        
        #update fidelity_settings
        self.fidelity_settings.update_prior(binary_result_fidelity,sampled_lf_settings)

        #step 5
        self.history.append({"iteration":self.train_iter,
                             "runid":runid,
                             "scenario":scenario_key,
                             "cost":cost,
                             "t_HF":t_HF,
                             "t_LF":t_LF,
                             "outcome_type":outcome_type,
                             "binary_result_scenario":binary_result_scenario,
                             "binary_result_fidelity":binary_result_fidelity,
                             "scenario_config":sampled_scenario_settings,
                             "hf_settings":self.hf_settings,
                             "lf_settings":sampled_lf_settings,
                             "scenario_settings_state":copy(self.scenarios),
                             "fidelity_settings_state":copy(self.fidelity_settings),
                             "compute_budget":self.compute_budget})
        
        with open("{}.pkl".format("./results/"+filename),"wb") as f:
            pickle.dump(self.history,f)
        
        #step 6
        print("Training iteration {}".format(self.train_iter))
        scenario_success_rate = np.mean([h["binary_result_scenario"] for h in self.history])
        fidelity_success_rate = np.mean([h["binary_result_fidelity"] for h in self.history])
        print("Scenario: {} - Cost: {} - Outcome Type: {} - Avg Scenario Success: {} - Avg Fidelity Success: {}".format(scenario_key,cost,outcome_type,scenario_success_rate,fidelity_success_rate))

        #step 7
        self.train_iter += 1

    # def train(self,n): #run n simulations
    #     for i in range(n):
    #         self.train_one_step_hf_lf()
    
    def mc_one_step_hf_lf(self,filename="log"): #evaluation of hf and lf, but no updating of parameters
        """
        1. randomly select one scenario 
        2. sample scenario_settings anf lf_settings via Thompson sampling
        3. run scenario using the self.run_hf_lf function
        4. Process the returns from self.run_hf_lf
            a. convert return_type ("TP","TN","FP","FN") and cost into success (return_type \in {"TP","TN"} \land cost<=self.compute_budget) or a failure
        5. Save all the results into a list of dictionaries {"iteration":self.train_iter,"runid":runid,"scenario":scenario_id,"cost":cost,"outcome_type":outcome_type,"scenario_config":scenario_config,"hf_config":hf_config,"lf_config":lf_config,"scenario_settings_state":copy(scenario_settings),"fidelity_settings_state":copy(fidelity_settings)}
        6. Print statistics
        7. Update self.train_iter
        """
        #step 1
        print("-"*80)
        scenario_key = random.choices(self.scenarios_keys,weights=[self.scenarios[k]["weight"] for k in self.scenarios_keys])[0]

        #step 2
        sampled_scenario_settings = self.scenarios[scenario_key]["settings"].sample_from_prior()
        sampled_lf_settings = self.fidelity_settings.sample_from_prior()    #for MC still sample don't update in step 4b

        #step 3
        cost, outcome_type, runid, t_HF, t_LF = self.run_hf_lf(self.scenarios[scenario_key]["scenario"],sampled_scenario_settings,self.hf_settings,sampled_lf_settings)

        #step 4a
        if np.logical_and(outcome_type in ["TP","TN"],cost<=self.compute_budget):
            #success for fidelity is if outcome_type in ["TP","TN"] and cost<=self.compute_budget
            binary_result_fidelity = 1
        elif np.logical_or(outcome_type in ["FP","FN"],cost>=self.compute_budget):
            binary_result_fidelity = 0
        else:
            raise ValueError("Returned outcome_type or cost are not of the expected value.")
        
        if outcome_type in ["TP","FN"]:
            #sucess for finding hard scenarios. In both "TP and "FN", the high-fidelity simulator found a failure is considered a success
            binary_result_scenario = 1
        elif outcome_type in ["TN","FP"]:
            binary_result_scenario = 0
        else:
            raise ValueError("outcome_type should be either 'TP', 'TN', 'FP', or 'FN'.")

        #step 4b
        #skip as we don't update


        #step 5
        self.history.append({"iteration":self.train_iter,
                             "runid":runid,
                             "scenario":scenario_key,
                             "cost":cost,
                             "t_HF":t_HF,
                             "t_LF":t_LF,
                             "outcome_type":outcome_type,
                             "binary_result_scenario":binary_result_scenario,
                             "binary_result_fidelity":binary_result_fidelity,
                             "scenario_config":sampled_scenario_settings,
                             "hf_settings":self.hf_settings,
                             "lf_settings":sampled_lf_settings,
                             "scenario_settings_state":copy(self.scenarios),
                             "fidelity_settings_state":copy(self.fidelity_settings),
                             "compute_budget":self.compute_budget})
        
        with open("{}.pkl".format("./results/"+filename),"wb") as f:
            pickle.dump(self.history,f)
        
        #step 6
        print("MC iteration {}".format(self.train_iter))
        scenario_success_rate = np.mean([h["binary_result_scenario"] for h in self.history])
        fidelity_success_rate = np.mean([h["binary_result_fidelity"] for h in self.history])
        print("Scenario: {} - Cost: {} - Outcome Type: {} - Avg Scenario Success: {} - Avg Fidelity Success: {}".format(scenario_key,cost,outcome_type,scenario_success_rate,fidelity_success_rate))

        #step 7
        self.train_iter += 1
    
    def eval_one_step_hf_lf(self,filename="log"): #evaluation of hf and lf, but no updating of parameters
        """
        1. randomly select one scenario 
        2. sample scenario_settings anf lf_settings via Thompson sampling
        3. run scenario using the self.run_hf_lf function
        4. Process the returns from self.run_hf_lf
            a. convert return_type ("TP","TN","FP","FN") and cost into success (return_type \in {"TP","TN"} \land cost<=self.compute_budget) or a failure
        5. Save all the results into a list of dictionaries {"iteration":self.train_iter,"runid":runid,"scenario":scenario_id,"cost":cost,"outcome_type":outcome_type,"scenario_config":scenario_config,"hf_config":hf_config,"lf_config":lf_config,"scenario_settings_state":copy(scenario_settings),"fidelity_settings_state":copy(fidelity_settings)}
        6. Print statistics
        7. Update self.train_iter
        """
        #step 1
        print("-"*80)
        scenario_key = random.choices(self.scenarios_keys,weights=[self.scenarios[k]["weight"] for k in self.scenarios_keys])[0]

        #step 2
        sampled_scenario_settings = self.scenarios[scenario_key]["settings"].sample_from_prior()
        sampled_lf_settings = self.fidelity_settings.get_map()   #don't sample, take greedy best result after training

        #step 3
        cost, outcome_type, runid, t_HF, t_LF = self.run_hf_lf(self.scenarios[scenario_key]["scenario"],sampled_scenario_settings,self.hf_settings,sampled_lf_settings)

        #step 4a
        if np.logical_and(outcome_type in ["TP","TN"],cost<=self.compute_budget):
            #success for fidelity is if outcome_type in ["TP","TN"] and cost<=self.compute_budget
            binary_result_fidelity = 1
        elif np.logical_or(outcome_type in ["FP","FN"],cost>=self.compute_budget):
            binary_result_fidelity = 0
        else:
            raise ValueError("Returned outcome_type or cost are not of the expected value.")
        
        if outcome_type in ["TP","FN"]:
            #sucess for finding hard scenarios. In both "TP and "FN", the high-fidelity simulator found a failure is considered a success
            binary_result_scenario = 1
        elif outcome_type in ["TN","FP"]:
            binary_result_scenario = 0
        else:
            raise ValueError("outcome_type should be either 'TP', 'TN', 'FP', or 'FN'.")

        #step 4b
        #skip as we don't update

        
        #step 5
        self.history.append({"iteration":self.train_iter,
                             "runid":runid,
                             "scenario":scenario_key,
                             "cost":cost,
                             "t_HF":t_HF,
                             "t_LF":t_LF,
                             "outcome_type":outcome_type,
                             "binary_result_scenario":binary_result_scenario,
                             "binary_result_fidelity":binary_result_fidelity,
                             "scenario_config":sampled_scenario_settings,
                             "hf_settings":self.hf_settings,
                             "lf_settings":sampled_lf_settings,
                             "scenario_settings_state":copy(self.scenarios),
                             "fidelity_settings_state":copy(self.fidelity_settings),
                             "compute_budget":self.compute_budget})
        
        with open("{}.pkl".format("./results/"+filename),"wb") as f:
            pickle.dump(self.history,f)
        
        #step 6
        print("Eval iteration {}".format(self.train_iter))
        scenario_success_rate = np.mean([h["binary_result_scenario"] for h in self.history])
        fidelity_success_rate = np.mean([h["binary_result_fidelity"] for h in self.history])
        print("Scenario: {} - Cost: {} - Outcome Type: {} - Avg Scenario Success: {} - Avg Fidelity Success: {}".format(scenario_key,cost,outcome_type,scenario_success_rate,fidelity_success_rate))

        #step 7
        self.train_iter += 1
    
    # def train_one_step_hf_scenario(self,filename="log"): #training to update the counts
    #     """
    #     1. randomly select one scenario 
    #     2. sample scenario_settings anf lf_settings via Thompson sampling
    #     3. run scenario using the self.run_hf_lf function
    #     4. Process the returns from self.run_hf
    #         a. convert return_type (0,1) into success or a failure
    #         b. update the scenario_settings but not lf settings
    #     5. Save all the results into a list of dictionaries {"iteration":self.train_iter,"runid":runid,"scenario":scenario_id,"cost":cost,"outcome_type":outcome_type,"scenario_config":scenario_config,"hf_config":hf_config,"scenario_settings_state":copy(scenario_settings),"fidelity_settings_state":copy(fidelity_settings)}
    #     6. Print statistics
    #     7. Update self.train_iter
    #     """
    #     #step 1
    #     print("-"*80)
    #     scenario_key = random.choices(self.scenarios_keys,weights=[self.scenarios[k]["weight"] for k in self.scenarios_keys])[0]

    #     #step 2
    #     sampled_scenario_settings = self.scenarios[scenario_key]["settings"].sample_from_prior()

    #     #step 3
    #     cost, outcome, runid = self.run_hf(self.scenarios[scenario_key]["scenario"],sampled_scenario_settings,self.hf_settings)

    #     #step 4a
    #     binary_result_scenario = outcome
        
        
    #     #step 4b
    #     #update scenario_settings
    #     self.scenarios[scenario_key]["settings"].update_prior(binary_result_scenario,sampled_scenario_settings)
    

    #     #step 5
    #     self.history.append({"iteration":self.train_iter,
    #                          "runid":runid,
    #                          "scenario":scenario_key,
    #                          "cost":cost,
    #                          "outcome_type":outcome,
    #                          "binary_result_scenario":binary_result_scenario,
    #                          "scenario_config":sampled_scenario_settings,
    #                          "hf_settings":self.hf_settings,
    #                          "scenario_settings_state":copy(self.scenarios),
    #                          "fidelity_settings_state":copy(self.fidelity_settings),
    #                          "compute_budget":self.compute_budget})
        
    #     with open("{}.pkl".format("./results/"+filename),"wb") as f:
    #         pickle.dump(self.history,f)
        
    #     #step 6
    #     print("Training iteration {}".format(self.train_iter))
    #     scenario_success_rate = np.mean([h["binary_result_scenario"] for h in self.history])
    #     print("Scenario: {} - Cost: {} - Outcome: {} - Avg Scenario Success: {}".format(scenario_key,cost,outcome,scenario_success_rate))

    #     #step 7
    #     self.train_iter += 1
    
    # def eval_one_step_hf(self,filename="log"): #training to update the counts
    #     """
    #     1. randomly select one scenario 
    #     2. sample scenario_settings via Thompson sampling
    #     3. run scenario using the self.run_hf function
    #     4. Process the returns from self.run_hf
    #         a. convert return_type (0,1) into success or a failure
    #     5. Save all the results into a list of dictionaries {"iteration":self.train_iter,"runid":runid,"scenario":scenario_id,"cost":cost,"outcome_type":outcome_type,"scenario_config":scenario_config,"hf_config":hf_config,"scenario_settings_state":copy(scenario_settings),"fidelity_settings_state":copy(fidelity_settings)}
    #     6. Print statistics
    #     7. Update self.train_iter
    #     """
    #     #step 1
    #     print("-"*80)
    #     scenario_key = random.choices(self.scenarios_keys,weights=[self.scenarios[k]["weight"] for k in self.scenarios_keys])[0]

    #     #step 2
    #     sampled_scenario_settings = self.scenarios[scenario_key]["settings"].sample_from_prior()

    #     #step 3
    #     cost, outcome, runid = self.run_hf(self.scenarios[scenario_key]["scenario"],sampled_scenario_settings,self.hf_settings)

    #     #step 4a
    #     binary_result_scenario = outcome
        
        
    #     #step 4b
    #     #don't update scenario_settings
    #     # self.scenarios[scenario_key]["settings"].update_prior(binary_result_scenario,sampled_scenario_settings)
    

    #     #step 5
    #     self.history.append({"iteration":self.train_iter,
    #                          "runid":runid,
    #                          "scenario":scenario_key,
    #                          "cost":cost,
    #                          "outcome_type":outcome,
    #                          "binary_result_scenario":binary_result_scenario,
    #                          "scenario_config":sampled_scenario_settings,
    #                          "hf_settings":self.hf_settings,
    #                          "scenario_settings_state":copy(self.scenarios),
    #                          "fidelity_settings_state":copy(self.fidelity_settings),
    #                          "compute_budget":self.compute_budget})
        
    #     with open("{}.pkl".format("./results/"+filename),"wb") as f:
    #         pickle.dump(self.history,f)
        
    #     #step 6
    #     print("Training iteration {}".format(self.train_iter))
    #     scenario_success_rate = np.mean([h["binary_result_scenario"] for h in self.history])
    #     print("Scenario: {} - Cost: {} - Outcome: {} - Avg Scenario Success: {}".format(scenario_key,cost,outcome,scenario_success_rate))

    #     #step 7
    #     self.train_iter += 1
    
    # def train_one_step_lf_scenario(self,filename="log"): #training to update the counts
    #     """
    #     1. randomly select one scenario 
    #     2. sample scenario_settings and lf_settings via Thompson sampling
    #     3. run scenario using the self.run_lf function
    #     4. Process the returns from self.run_lf
    #         a. convert return_type (0,1) into success or a failure
    #         b. update scenario settings
    #     5. Save all the results into a list of dictionaries {"iteration":self.train_iter,"runid":runid,"scenario":scenario_id,"cost":cost,"outcome_type":outcome_type,"scenario_config":scenario_config,"lf_config":lf_config,"scenario_settings_state":copy(scenario_settings),"fidelity_settings_state":copy(fidelity_settings)}
    #     6. Print statistics
    #     7. Update self.train_iter
    #     """
    #     #step 1
    #     print("-"*80)
    #     scenario_key = random.choices(self.scenarios_keys,weights=[self.scenarios[k]["weight"] for k in self.scenarios_keys])[0]

    #     #step 2
    #     sampled_scenario_settings = self.scenarios[scenario_key]["settings"].sample_from_prior()
    #     sampled_lf_settings = self.fidelity_settings.get_map()   #don't sample, take greedy best result after training

    #     #step 3
    #     cost, outcome, runid = self.run_lf(self.scenarios[scenario_key]["scenario"],sampled_scenario_settings,sampled_lf_settings)

    #     #step 4a
    #     binary_result_scenario = outcome
        
        
    #     #step 4b
    #     #update scenario_settings
    #     self.scenarios[scenario_key]["settings"].update_prior(binary_result_scenario,sampled_scenario_settings)
    

    #     #step 5
    #     self.history.append({"iteration":self.train_iter,
    #                          "runid":runid,
    #                          "scenario":scenario_key,
    #                          "cost":cost,
    #                          "outcome_type":outcome,
    #                          "binary_result_scenario":binary_result_scenario,
    #                          "scenario_config":sampled_scenario_settings,
    #                          "lf_settings":sampled_lf_settings,
    #                          "scenario_settings_state":copy(self.scenarios),
    #                          "fidelity_settings_state":copy(self.fidelity_settings),
    #                          "compute_budget":self.compute_budget})
        
    #     with open("{}.pkl".format("./results/"+filename),"wb") as f:
    #         pickle.dump(self.history,f)
        
    #     #step 6
    #     print("Training iteration {}".format(self.train_iter))
    #     scenario_success_rate = np.mean([h["binary_result_scenario"] for h in self.history])
    #     print("Scenario: {} - Cost: {} - Outcome: {} - Avg Scenario Success: {}".format(scenario_key,cost,outcome,scenario_success_rate))

    #     #step 7
    #     self.train_iter += 1
    
    # def eval_one_step_lf(self,filename="log"): #training to update the counts
    #     """
    #     1. randomly select one scenario 
    #     2. sample scenario_settings and lf_settings via MAP
    #     3. run scenario using the self.run_lf function
    #     4. Process the returns from self.run_lf
    #         a. convert return_type (0,1) into success or a failure
    #     5. Save all the results into a list of dictionaries {"iteration":self.train_iter,"runid":runid,"scenario":scenario_id,"cost":cost,"outcome_type":outcome_type,"scenario_config":scenario_config,"lf_config":lf_config,"scenario_settings_state":copy(scenario_settings),"fidelity_settings_state":copy(fidelity_settings)}
    #     6. Print statistics
    #     7. Update self.train_iter
    #     """
    #     #step 1
    #     print("-"*80)
    #     scenario_key = random.choices(self.scenarios_keys,weights=[self.scenarios[k]["weight"] for k in self.scenarios_keys])[0]

    #     #step 2
    #     sampled_scenario_settings = self.scenarios[scenario_key]["settings"].sample_from_prior()
    #     sampled_lf_settings = self.fidelity_settings.get_map()   #don't sample, take greedy best result after training

    #     #step 3
    #     cost, outcome, runid = self.run_lf(self.scenarios[scenario_key]["scenario"],sampled_scenario_settings,sampled_lf_settings)

    #     #step 4a
    #     binary_result_scenario = outcome
        
        
    #     #step 4b
    #     #update scenario_settings
    #     # self.scenarios[scenario_key]["settings"].update_prior(binary_result_scenario,sampled_scenario_settings)
    

    #     #step 5
    #     self.history.append({"iteration":self.train_iter,
    #                          "runid":runid,
    #                          "scenario":scenario_key,
    #                          "cost":cost,
    #                          "outcome_type":outcome,
    #                          "binary_result_scenario":binary_result_scenario,
    #                          "scenario_config":sampled_scenario_settings,
    #                          "lf_settings":sampled_lf_settings,
    #                          "scenario_settings_state":copy(self.scenarios),
    #                          "fidelity_settings_state":copy(self.fidelity_settings),
    #                          "compute_budget":self.compute_budget})
        
    #     with open("{}.pkl".format("./results/"+filename),"wb") as f:
    #         pickle.dump(self.history,f)
        
    #     #step 6
    #     print("Training iteration {}".format(self.train_iter))
    #     scenario_success_rate = np.mean([h["binary_result_scenario"] for h in self.history])
    #     print("Scenario: {} - Cost: {} - Outcome: {} - Avg Scenario Success: {}".format(scenario_key,cost,outcome,scenario_success_rate))

    #     #step 7
    #     self.train_iter += 1

    
    # def meta_test_train_hf(self,n,filename="log"):
    #     start_time = time.time()
    #     for i in tqdm(range(n)):
    #         self.train_one_step_hf_scenario(filename=filename)
        
    #     #save the last scenario_settings
    #     with open("{}.pkl".format("./results/"+filename+"_final_scenario_settings"),"wb") as f:
    #         pickle.dump(self.scenarios,f)
        
    #     self.history = []
    #     self.train_iter = 0
    #     end_time = time.time()
    #     print("Entire Simulation Time: ",end_time-start_time)

    # def meta_test_eval_hf(self,n,filename="log"):
    #     start_time = time.time()
    #     for i in tqdm(range(n)):
    #         self.eval_one_step_hf(filename=filename)
        
    #     self.history = []
    #     self.train_iter = 0
    #     end_time = time.time()
    #     print("Entire Simulation Time: ",end_time-start_time)
    
    # def meta_test_train_lf(self,n,filename="log"):
    #     start_time = time.time()
    #     for i in tqdm(range(n)):
    #         self.train_one_step_lf_scenario(filename=filename)
        
    #     #save the last scenario_settings
    #     with open("{}.pkl".format("./results/"+filename+"_final_scenario_settings"),"wb") as f:
    #         pickle.dump(self.scenarios,f)
        
    #     self.history = []
    #     self.train_iter = 0
    #     end_time = time.time()
    #     print("Entire Simulation Time: ",end_time-start_time)

    # def meta_test_eval_lf(self,n,filename="log"):
    #     start_time = time.time()
    #     for i in tqdm(range(n)):
    #         self.eval_one_step_lf(filename=filename)
        
    #     self.history = []
    #     self.train_iter = 0
    #     end_time = time.time()
    #     print("Entire Simulation Time: ",end_time-start_time)

    def train(self,n,filename="log"): #run n simulations
        start_time = time.time()
        for i in tqdm(range(n)):
            self.train_one_step_hf_lf(filename=filename)
        
        #save the last scenario_settings and fidelity settings
        with open("{}.pkl".format("./results/"+filename+"_final_scenario_settings"),"wb") as f:
            pickle.dump(self.scenarios,f)

        with open("{}.pkl".format("./results/"+filename+"_final_fidelity_settings"),"wb") as f:
            pickle.dump(self.fidelity_settings,f)

        self.history = []
        self.train_iter = 0
        end_time = time.time()
        print("Entire Simulation Time: ",end_time-start_time)

    def mc(self,n,filename="log"): #run n simulations
        start_time = time.time()
        for i in tqdm(range(n)):
            self.mc_one_step_hf_lf(filename=filename)
        self.history = []
        self.train_iter = 0
        end_time = time.time()
        print("Entire Simulation Time: ",end_time-start_time)

    def eval(self,n,filename="log"): #run n simulations
        start_time = time.time()
        for i in tqdm(range(n)):
            self.eval_one_step_hf_lf(filename=filename)
        self.history = []
        self.train_iter = 0
        end_time = time.time()
        print("Entire Simulation Time: ",end_time-start_time)
    
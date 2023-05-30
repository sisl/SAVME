import pickle

from SAVME.settings import Settings
from SAVME.meta_env import MetaEnv, load_from_file
from SAVME.simulator_interface import run_hf_lf

from scenarios.av_left_cv_straight_opp_direction import AVLeftCVStraightOppDirectionScenario
from scenarios.av_left_cv_straight_same_direction import AVLeftCVStraightSameDirectionScenario
from scenarios.cv_left_av_straight_opp_direction import CVLeftAVStraightOppDirectionScenario
from scenarios.cv_left_av_straight_same_direction import CVLeftAVStraightSameDirectionScenario
from scenarios.av_cut_in import AVCutInScenario
from scenarios.cv_cut_in import CVCutInScenario
from scenarios.cv_stop import CVStopScenario
from scenarios.parking_lot_backup import ParkingLotBackupScenario
from scenarios.av_merge_right import AVMergeRightScenario
from scenarios.cv_backup_one_way import CVBackupOneWayScenario
from scenarios.utils import *

scenarios = {"av_left_cv_straight_opp_direction": AVLeftCVStraightOppDirectionScenario(),
             "av_left_cv_straight_same_direction": AVLeftCVStraightSameDirectionScenario(),
             "cv_left_av_straight_opp_direction": CVLeftAVStraightOppDirectionScenario(),
             "cv_left_av_straight_same_direction": CVLeftAVStraightSameDirectionScenario(),
             "av_cut_in":AVCutInScenario(),
             "cv_cut_in":CVCutInScenario(),
             "cv_stop":CVStopScenario(),
             "parking_lot_backup":ParkingLotBackupScenario()}

scenarios_meta_test = {"av_merge_right": AVMergeRightScenario(),
                       "cv_backup_one_way":CVBackupOneWayScenario()}
    
scenarios_with_config = {name:{"scenario":scenarios[name],"settings":Settings(scenarios[name].get_constraints()),"weight":1/len(scenarios)} for name in scenarios.keys()}

scenarios_meta_test_with_config = {name:{"scenario":scenarios_meta_test[name],"settings":Settings(scenarios_meta_test[name].get_constraints()),"weight":1/len(scenarios_meta_test)} for name in scenarios_meta_test.keys()}

#{name:{"var_type":var_type,"values":values,"bins":bins,"bin_edge_type":bin_edge_type,"prior":prior}}
fidelity_settings_config = {"camera_view_distance":{"var_type":"continuous","values":(10,5000),"bin_edge_type":"log"}, 
                    "camera_bloom_level":{"var_type":"discrete","values":("HIGH","LOW")},
                    "camera_bloom_disable":{"var_type":"discrete","values":("true","false")},
                    "camera_disable_lighting":{"var_type":"discrete","values":("true","false")},
                    "camera_disable_shadows":{"var_type":"discrete","values":("true","false")},
                    "camera_disable_models":{"var_type":"discrete","values":("true","false")},   #fog, lens, etc.
                    "camera_disable_depth_of_field":{"var_type":"discrete","values":("true","false")},
                    "camera_near_clipping_distance":{"var_type":"continuous","values":(0.2,20),"bin_edge_type":"log"},  
                    "camera_disable_shot_noise":{"var_type":"discrete","values":("true","false")},
                    "lidar_disable_shot_noise":{"var_type":"discrete","values":("true","false")},
                    "lidar_enable_ambient":{"var_type":"discrete","values":("true","false")},
                    "lidar_disable_translucency":{"var_type":"discrete","values":("true","false")},
                    "lidar_subsample_count":{"var_type":"discrete","values":(1,2,3,4,5)},
                    "lidar_near_clipping_distance":{"var_type":"continuous","values":(0.2,20),"bin_edge_type":"log"}, 
                    "lidar_raytracing_bounces":{"var_type":"discrete","values":(0,1,2,3,4)},
                    "FREQUENCY":{"var_type":"discrete","values":(2,4,6,8,10)}    #for now there is only one option for the frequency until we have determinedS
                    }
fidelity_settings = Settings(fidelity_settings_config)

# # #Train 500 all scenarios all frequencies
# meta_env = MetaEnv(scenarios_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.5)
# meta_env.train(500,filename="001")
# meta_env.eval(100,filename="002")
# # meta_env = load_from_file("./results/001.pkl",run_hf_lf,compute_budget=0.3)

# #Train 500 all scenarios all frequencies
# meta_env = MetaEnv(scenarios_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.4)
# meta_env.train(500,filename="007")
# meta_env = load_from_file("./results/005.pkl",run_hf_lf,compute_budget=0.4)
# meta_env.train_iter = 0
# meta_env.history = []
# meta_env.eval(100,filename="008")
# meta_env = load_from_file("./results/001.pkl",run_hf_lf,compute_budget=0.3)


#Baseline MC 500 runs
# meta_env = MetaEnv(scenarios_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.4)
# meta_env.mc(500,"009_3")

# meta_env = MetaEnv(scenarios_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.2)
# meta_env.train(500,filename="012")
# meta_env.eval(100,filename="013")

# meta_env = MetaEnv(scenarios_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.25)
# meta_env.train(500,filename="014")
# meta_env.eval(100,filename="015")

# meta_env = MetaEnv(scenarios_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.4)
# meta_env.mc(100,"999_backup_one_way")

#####################################################
#meta-testing

# #high-fidelity run

# meta_env_hf = MetaEnv(scenarios_meta_test_with_config,high_fidelity_settings,None,run_hf_lf,run_hf,run_lf,compute_budget=0.3)
# print("High-Fidelity Meta Testing")
# print("training")
# meta_env_hf.meta_test_train_hf(200,"016_hf")
# print("evaluation")
# meta_env_hf.meta_test_eval_hf(100,"017_hf")
# print("stop")

# #low-fidelity_run
# #load 010 model
# print("Low-Fidelity Meta Testing")
# with open("./results/010.pkl","rb") as f:
#     data = pickle.load(f)
# extracted_fidelity_settings = data[-1]["fidelity_settings_state"]
# meta_env_lf = MetaEnv(scenarios_meta_test_with_config,None,extracted_fidelity_settings,run_hf_lf,run_hf,run_lf,compute_budget=0.3)
# print("training")
# meta_env_lf.meta_test_train_lf(200,"016_lf")
# meta_env_lf.meta_test_eval_lf(100,"017_lf")
# print("testing")


# #################OLD META-TESTING########################################
# #high-fidelity run

# meta_env_hf = MetaEnv(scenarios_meta_test_with_config,high_fidelity_settings,None,run_hf_lf,run_hf,run_lf,compute_budget=0.4)
# print("High-Fidelity Meta Testing")
# print("training")
# meta_env_hf.meta_test_train_hf(200,"018_hf")
# print("evaluation")
# meta_env_hf.meta_test_eval_hf(100,"019_hf")
# print("stop")

# #low-fidelity_run
# #load 010 model
# print("Low-Fidelity Meta Testing")
# with open("./results/007.pkl","rb") as f:
#     data = pickle.load(f)
# extracted_fidelity_settings = data[-1]["fidelity_settings_state"]
# meta_env_lf = MetaEnv(scenarios_meta_test_with_config,None,extracted_fidelity_settings,run_hf_lf,run_hf,run_lf,compute_budget=0.4)
# print("training")
# meta_env_lf.meta_test_train_lf(200,"018_lf")
# meta_env_lf.meta_test_eval_lf(100,"019_lf")
# print("testing")

#MC BASELINE on TEST SCENARIOS
meta_env = MetaEnv(scenarios_meta_test_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.3)
meta_env.mc(200,"023")

# # #RE-RUNS
# meta_env = MetaEnv(scenarios_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.4)
# meta_env.train(500,"007_C")
# meta_env.eval(100,"008_C")

# meta_env = MetaEnv(scenarios_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.3)
# meta_env.train(500,"010_C")
# meta_env.eval(100,"011_C")

meta_env = MetaEnv(scenarios_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.2)
meta_env.train(500,"012_C")
meta_env.eval(100,"013_C")

####################NEW META-TESTING################################################
#######020########
#starting from scratch
meta_env_no_prior = MetaEnv(scenarios_meta_test_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.3)
meta_env_no_prior.train(200,"020_C_no_prior_train")
# meta_env_no_prior = load_from_file("./results/020_B_no_prior_train.pkl",run_hf_lf,compute_budget=0.3)
# meta_env_no_prior.train_iter = 0
# meta_env_no_prior.history = []
meta_env_no_prior.eval(100,"020_C_no_prior_eval")

#starting with prior
with open("./results/010_C.pkl","rb") as f:   #010 is the training with budget 0.3
    data = pickle.load(f)

extracted_fidelity_settings = data[-1]["fidelity_settings_state"]
meta_env_w_prior = MetaEnv(scenarios_meta_test_with_config,high_fidelity_settings,extracted_fidelity_settings,run_hf_lf,compute_budget=0.3)
meta_env_w_prior.train(200,"020_C_w_prior_train")
meta_env_w_prior.eval(100,"020_C_w_prior_eval")

#######021########
#starting from scratch
meta_env_no_prior = MetaEnv(scenarios_meta_test_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.4)
meta_env_no_prior.train(200,"021_C_no_prior_train")
meta_env_no_prior.eval(100,"021_C_no_prior_eval")

#starting with prior
with open("./results/007_C.pkl","rb") as f:   #007 is the training with budget 0.4
    data = pickle.load(f)

extracted_fidelity_settings = data[-1]["fidelity_settings_state"]
meta_env_w_prior = MetaEnv(scenarios_meta_test_with_config,high_fidelity_settings,extracted_fidelity_settings,run_hf_lf,compute_budget=0.4)
meta_env_w_prior.train(200,"021_C_w_prior_train")
meta_env_w_prior.eval(100,"021_C_w_prior_eval")

#######022########
#starting from scratch
meta_env_no_prior = MetaEnv(scenarios_meta_test_with_config,high_fidelity_settings,fidelity_settings,run_hf_lf,compute_budget=0.2)
meta_env_no_prior.train(200,"022_C_no_prior_train")
meta_env_no_prior.eval(100,"022_C_no_prior_eval")

#starting with prior
with open("./results/012_C.pkl","rb") as f:   #012 is the training with budget 0.2
    data = pickle.load(f)

extracted_fidelity_settings = data[-1]["fidelity_settings_state"]
meta_env_w_prior = MetaEnv(scenarios_meta_test_with_config,high_fidelity_settings,extracted_fidelity_settings,run_hf_lf,compute_budget=0.2)
meta_env_w_prior.train(200,"022_C_w_prior_train")
meta_env_w_prior.eval(100,"022_C_w_prior_eval")

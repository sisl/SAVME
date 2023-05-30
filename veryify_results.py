import pickle
import numpy as np

check_file = "./results/008.pkl"

compute_budget = 0.4

with open(check_file,"rb") as f:
    data = pickle.load(f)
print(data.__len__())

if compute_budget is None:
    compute_budget = data[-1]["compute_budget"]

outcome_type = [d["outcome_type"] for d in data]
tp = set(np.where(np.array(outcome_type)=="TP")[0])
tn = set(np.where(np.array(outcome_type)=="TN")[0])
fp = set(np.where(np.array(outcome_type)=="FP")[0])
fn = set(np.where(np.array(outcome_type)=="FN")[0])

cost = [d["cost"] for d in data]
satisfied_c_budget = set(np.where(np.array(cost)<=compute_budget)[0])
print("c_ratio: ",len(satisfied_c_budget)/len(cost))

#check for scenario success
print("Scenario Success Rate: ",len(tp.union(fn))/len(outcome_type))
print("TP Rate: ",len(tp)/len(outcome_type))
print("TN Rate: ",len(tn)/len(outcome_type))
print("FP Rate: ",len(fp)/len(outcome_type))
print("FN Rate: ",len(fn)/len(outcome_type))

#check fidelity
print("Fidelity Success Rate: ",len((tp.union(tn)).intersection(satisfied_c_budget))/len(outcome_type))
print("Average Cost: ",np.mean(cost))

#read out fidelity settings
print("-"*80)
print("Settings")
keys = list(data[-1]["lf_settings"].keys())
for k in keys:
    print("{} - {} - {}".format(k,data[-1]["hf_settings"][k],data[-1]["fidelity_settings_state"].get_map()[k]))

# #read out scenario map
# scenarios = list(data[-1]["scenario_settings_state"].keys())
# for s in scenarios:
#     print("-"*80)
#     print(s)
#     keys = list(data[-1]["scenario_settings_state"][s]["settings"].variables.keys())
#     for k in keys:
#         print("{} - {}".format(k,data[-1]["scenario_settings_state"][s]["settings"].variables[k].get_map()))
print("stop")
import pickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from tqdm import tqdm

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif"
})

check_file = "./results/013_C.pkl"
hf_mc_file = "./results/009.pkl"
train_file = "./results/012_C.pkl"


compute_budget = 0.25

with open(check_file,"rb") as f:
    data = pickle.load(f)

with open(hf_mc_file,"rb") as f:
    data_hf = pickle.load(f)

with open(train_file,"rb") as f:
    data_train = pickle.load(f)

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
# lf_scenario_success_rate = len(tp.union(fn))/len(outcome_type)
lf_scenario_success_rate = len(tp)/len(outcome_type)
print("Scenario Success Rate: ",lf_scenario_success_rate)
print("TP Rate: ",len(tp)/len(outcome_type))
print("TN Rate: ",len(tn)/len(outcome_type))
print("FP Rate: ",len(fp)/len(outcome_type))
print("FN Rate: ",len(fn)/len(outcome_type))

#check fidelity
print("Fidelity Success Rate: ",len((tp.union(tn)).intersection(satisfied_c_budget))/len(outcome_type))
avg_cost_lf  = np.mean(cost)
print("Average Cost: ",avg_cost_lf)

#speedup vs hf
outcome_type_hf = [d["outcome_type"] for d in data_hf]
failure_sequence_hf_mc = []
for d in data_hf:
    if d["outcome_type"] in ["TP","FN"]:    #This for the MC sampling so TP and FN are valid
        failure_sequence_hf_mc.append(True)
    else:
        failure_sequence_hf_mc.append(False)
tp_hf = set(np.where(np.array(outcome_type_hf)=="TP")[0])
tn_hf = set(np.where(np.array(outcome_type_hf)=="TN")[0])
fp_hf = set(np.where(np.array(outcome_type_hf)=="FP")[0])
fn_hf = set(np.where(np.array(outcome_type_hf)=="FN")[0])
scenario_success_rate_hf_mc = len(tp_hf.union(fn_hf))/len(outcome_type_hf)  #This is for MC sampling, so TP and FN are valid
print("HF_MC scenario success rate: ",scenario_success_rate_hf_mc)
speedup = lf_scenario_success_rate / scenario_success_rate_hf_mc / avg_cost_lf
print("Seedup factor vs HF MC: ",speedup)
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


#breakeven calculations
# failure_rate_hc_mc = scenario_success_rate_hf_mc
# x = np.linspace(0,499,500)
# y = np.interp(x,[0,500],[0,failure_rate_hc_mc*500])
#find actual times for HF
HF_times = []
for d in tqdm(data_hf):
    runid = d["runid"]
    with open("./logs/{}/{}_HF.pkl".format(runid,runid),"rb") as f:
        raw = pickle.load(f)
    HF_times.append(raw[2])


fig,axs = plt.subplots(1,1,figsize=(5,3.5))

# axs.plot(x,y,label="high-fidelity MC sampling",c='#0072C6')


train_files = ["./results/007.pkl","./results/010.pkl","./results/012.pkl"]
budgets = [0.4,0.3,0.2]
colors = ['#6a001f', '#ff8e00','#83aafa',]
HF_surrogate_times = []

for train_file, budget,c in tqdm(zip(train_files,budgets,colors)):
    with open(train_file,"rb") as f:
        data_train = pickle.load(f)

    found_failure = []
    cost_train = []
    special_hf_time = []
    for d in data_train:
        if d["outcome_type"] in ["TP"]:
            found_failure.append(True)
        else:
            found_failure.append(False)
        
        #get cost
        runid = d["runid"]
        #hf time
        with open("./logs/{}/{}_HF.pkl".format(runid,runid),"rb") as f:
            raw = pickle.load(f)
        HF_time = raw[2]
        #lf time
        with open("./logs/{}/{}_LF.pkl".format(runid,runid),"rb") as f:
            raw = pickle.load(f)
        LF_time = raw[2]

        cost_train.append(HF_time + LF_time)
        special_hf_time.append(HF_time)
    HF_surrogate_times.append(special_hf_time)

    axs.plot(np.cumsum(cost_train)/60,np.cumsum(found_failure),label=r"$C_{{\mathrm{{budget}}}}={}$".format(budget),c=c)

HF_times = np.mean(HF_surrogate_times,axis=0)
axs.plot(np.cumsum(HF_times)/60,np.cumsum(failure_sequence_hf_mc),label="baseline",c='#53565a')
legend = axs.legend()
legend.get_frame().set_alpha(1)  # Set the transparency to 1 (non-transparent)
legend.get_frame().set_linewidth(0.5)  # Set the linewidth to 1 (black line)
legend.get_frame().set_edgecolor('black')  # Set the edgecolor to black
legend.get_frame().set_linestyle('-')  # Set the linestyle to solid
legend.get_frame().set_boxstyle("square",pad=0)
axs.set_xlabel("meta-training time [min]")
axs.set_ylabel("\# found failures")
axs.grid(which="both")
fig.tight_layout()
for axis in ['top','bottom','left','right']:
    axs.spines[axis].set_linewidth(1)
fig.savefig("meta_training_breakeven.pdf")
print("stop")
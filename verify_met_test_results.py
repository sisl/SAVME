import numpy as np
import pickle
from tqdm import tqdm
import matplotlib.pyplot as plt

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif"
})

##########################################################################################
##################THIS SECTION IS FOR THE TEST EVALS######################################
##########################################################################################
prior_file = './results/021_2_w_prior_eval.pkl'
no_prior_file = './results/021_2_no_prior_eval.pkl'
BUDGET = 0.4

with open(prior_file,"rb") as f:
    data_prior = pickle.load(f)

with open(no_prior_file,"rb") as f:
    data_no_prior = pickle.load(f)

#get TP rates
outcome_types_prior = [d["outcome_type"] for d in data_prior]
cost_prior = [d["cost"] for d in data_prior]
outcome_types_no_prior = [d["outcome_type"] for d in data_no_prior]
cost_no_prior = [d["cost"] for d in data_no_prior]

tp_rate_prior = len(set(np.where(np.array(outcome_types_prior)=="TP")[0]))/len(outcome_types_prior)
tn_rate_prior = len(set(np.where(np.array(outcome_types_prior)=="TN")[0]))/len(outcome_types_prior)
fp_rate_prior = len(set(np.where(np.array(outcome_types_prior)=="FP")[0]))/len(outcome_types_prior)
fn_rate_prior = len(set(np.where(np.array(outcome_types_prior)=="FN")[0]))/len(outcome_types_prior)

tp_rate_no_prior = len(set(np.where(np.array(outcome_types_no_prior)=="TP")[0]))/len(outcome_types_no_prior)
tn_rate_no_prior = len(set(np.where(np.array(outcome_types_no_prior)=="TN")[0]))/len(outcome_types_no_prior)
fp_rate_no_prior = len(set(np.where(np.array(outcome_types_no_prior)=="FP")[0]))/len(outcome_types_no_prior)
fn_rate_no_prior = len(set(np.where(np.array(outcome_types_no_prior)=="FN")[0]))/len(outcome_types_no_prior)

print("TP rates: Prior: {} - No prior: {}".format(tp_rate_prior,tp_rate_no_prior))
print("TN rates: Prior: {} - No prior: {}".format(tn_rate_prior,tn_rate_no_prior))
print("FP rates: Prior: {} - No prior: {}".format(fp_rate_prior,fp_rate_no_prior))
print("FN rates: Prior: {} - No prior: {}".format(fn_rate_prior,fn_rate_no_prior))
print("Avg Cost: Prior: {} - No prior: {}".format(np.mean(cost_prior),np.mean(cost_no_prior)))


##########################################################################################
##################THIS SECTION IS FOR THE TEST TRAINING###################################
##########################################################################################
fig,axs = plt.subplots(1,1,figsize=(5,3.5))

# colors_dict = {"poppy": "#E98300",
#                "poppy light": "#FFC757",
#                "cardinal": "#8C1515",
#                "cardinal light": "#FFA08C",
#                "dark sky": "#016895",
#                "light sky": "#92D6FF",
#                "cool grey": "#53565A"}

colors_dict = {"purple": "#BD0060",
               "purple light": "#FF95CE",
               "blue": "#0071D0",
               "blue light": "#9CD4FF",
               "green": "#006B00",
               "green light": "#90E378",
               "cool grey": "#53565A"}

train_files = ["./results/021_2_w_prior_train.pkl","./results/021_2_no_prior_train.pkl",
               "./results/020_w_prior_train.pkl","./results/020_no_prior_train.pkl",
               "./results/022_w_prior_train.pkl","./results/022_no_prior_train.pkl",
               "./results/023.pkl"]
labels = [r"$C_{\mathrm{b.}}=0.4$, M.-T. prior",r"$C_{\mathrm{b.}}=0.4$, uniform prior",
          r"$C_{\mathrm{b.}}=0.3$, M.-T. prior",r"$C_{\mathrm{b.}}=0.3$, uniform prior",
          r"$C_{\mathrm{b.}}=0.2$, M.-T. prior",r"$C_{\mathrm{b.}}=0.2$, uniform prior",
          "baseline"]
# colors = ['#6CC0E5','#008080']
# colors = ['#344BC2','#86B1DA','#F5A400','#FAB96F','#C71A1D','#FA7474']

colors = ['#6a001f','#6a001f', '#ff8e00','#ff8e00', '#83aafa','#83aafa','#53565a']
baseline_binary = [0,0,0,0,0,0,1]
uniform_binary = [0,1,0,1,0,1,0]

for train_file, label,c,baseline,uniform in tqdm(zip(train_files,labels,colors,baseline_binary,uniform_binary)):
    with open(train_file,"rb") as f:
        data_train = pickle.load(f)

    found_failure = []
    cost_train = []
    hf_times = []
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
        hf_times.append(HF_time)

    if baseline:
        print("SLOPE BASELINE:",(np.cumsum(found_failure)[-1])/(np.cumsum(hf_times)[-1]/60))
        axs.plot(np.cumsum(hf_times)/60,np.cumsum(found_failure),label=label,c=c)
    else:
        if uniform:
            print("SLOPE:",(np.cumsum(found_failure)[-1])/(np.cumsum(cost_train)[-1]/60))
            axs.plot(np.cumsum(cost_train)/60,np.cumsum(found_failure),"--",label=label,c=c)
        else:
            print("SLOPE:",(np.cumsum(found_failure)[-1])/(np.cumsum(cost_train)[-1]/60))
            axs.plot(np.cumsum(cost_train)/60,np.cumsum(found_failure),label=label,c=c)
    print("Runtime {}: {}".format(label,np.cumsum(cost_train)[-1]))

legend = axs.legend()
legend.get_frame().set_alpha(1)  # Set the transparency to 1 (non-transparent)
legend.get_frame().set_linewidth(0.5)  # Set the linewidth to 1 (black line)
legend.get_frame().set_edgecolor('black')  # Set the edgecolor to black
legend.get_frame().set_linestyle('-')  # Set the linestyle to solid
legend.get_frame().set_boxstyle("square",pad=0)
axs.set_xlabel("meta-testing time [min]")
axs.set_ylabel("\# found failures")
axs.set_ylim(-10,200)
axs.grid(which="both")
fig.tight_layout()
for axis in ['top','bottom','left','right']:
    axs.spines[axis].set_linewidth(1)
fig.savefig("meta_testing.pdf")
print("stop")



print("stop")

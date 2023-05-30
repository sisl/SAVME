import numpy as np
import matplotlib.pyplot as plt
import pickle


files = [["./results/009.pkl"],
         ["./results/007.pkl","./results/007_B.pkl","./results/007_C.pkl"],
         ["./results/010.pkl","./results/010_B.pkl","./results/010_C.pkl"],
         ["./results/012.pkl","./results/012_B.pkl","./results/012_C.pkl"]] 

time_series_extracted = []
HF_surrogate_times = []

for outer in files:
    print(outer)

    inner_time_series = []

    for train_file in outer:
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
        inner_time_series.append({"t":cost_train,"failure":found_failure})
        HF_surrogate_times.append(special_hf_time)
    time_series_extracted.append(inner_time_series)



#######AVERAGE SERIES##########
averaged_costs = []
averaged_failures = []
mean_final_costs = []
mean_final_failures = []
std_final_costs = []
std_final_failures = []


for inner in time_series_extracted:
    averaged_costs.append(np.mean([d["t"] for d in inner],axis=0))
    averaged_failures.append(np.mean([d["failure"] for d in inner],axis=0))
    std_final_costs.append(np.std([np.cumsum(d["t"])[-1]/60 for d in inner]))
    std_final_failures.append(np.std([np.cumsum(d["failure"])[-1] for d in inner]))
    mean_final_costs.append(np.mean([np.cumsum(d["t"])[-1]/60 for d in inner]))
    mean_final_failures.append(np.mean([np.cumsum(d["failure"])[-1] for d in inner]))

hf_times = np.mean(HF_surrogate_times,axis=0)


#################PLOT###########
plt.plot(np.cumsum(hf_times)/60,np.cumsum(averaged_failures[0]),label="baseline")
plt.plot(np.cumsum(averaged_costs[1])/60,np.cumsum(averaged_failures[1]),label="0.4")
plt.errorbar(mean_final_costs[1],mean_final_failures[1],std_final_failures[1],std_final_costs[1],c="#000000",capsize=3,alpha=0.5)
plt.plot(np.cumsum(averaged_costs[2])/60,np.cumsum(averaged_failures[2]),label="0.3")
plt.errorbar(mean_final_costs[2],mean_final_failures[2],std_final_failures[2],std_final_costs[2],c="#000000",capsize=3,alpha=0.5)
plt.plot(np.cumsum(averaged_costs[3])/60,np.cumsum(averaged_failures[3]),label="0.2")
plt.errorbar(mean_final_costs[3],mean_final_failures[3],std_final_failures[3],std_final_costs[3],c="#000000",capsize=3,alpha=0.5)
plt.legend()
plt.show()

print("stop")




    # axs.plot(np.cumsum(cost_train)/60,np.cumsum(found_failure),label=r"$C_{{\mathrm{{budget}}}}={}$".format(budget),c=c)
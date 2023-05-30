import torch
import numpy as np

class Variable(object):
    def __init__(self,name,var_type,values,bins=5,bin_edge_type="linear",prior="uniform") -> None:
        self.name = name
        self.type = var_type
        self.values = values    #in case of var_type continuous, this will be the range, in case of var_type discrete, this will be the category labels
        self.bins = bins
        self.bin_edge_type = bin_edge_type  #only used when continuous for edge determination. If "linear", bin edges will be linearly chosen between the lower and upper bounds, in case of "log" a log scaling will be applied
        self.prior = prior
        self._initial_values()
        self._apply_prior()
    
    def _initial_values(self):
        if self.type == "discrete":
            self.bin_edges = self.values   #using the values as the actual bins
            self.bins = len(self.values)    #update the self.bins to contain the number of class variables
            self.counts = {v:np.zeros(2) for v in self.values}    
        elif self.type == "continuous":
            #currently, we need to digitize continuous ranges, so they are only pseudo-continuous
            if self.bin_edge_type == "linear":
                bin_width = (self.values[1]-self.values[0])/self.bins
                self.bin_edges = np.array([self.values[0] + i*bin_width for i in range(self.bins + 1)])    #defines the bin edges
                self.counts = {v:np.zeros(2) for v in range(1,self.bins+1)} 
            elif self.bin_edge_type == "log":
                lower_bound_scaled = 1 #choose arbitrary positive lower bound for log scaling
                upper_bound_scaled = self.values[1] - self.values[0] + 1
                log10_lower_bound_scaled = np.log10(lower_bound_scaled)
                log10_upper_bound_scaled = np.log10(upper_bound_scaled)
                log10_bin_width = (log10_upper_bound_scaled - log10_lower_bound_scaled) / self.bins
                log10_bin_boundaries = np.array([log10_lower_bound_scaled + i*log10_bin_width for i in range(self.bins + 1)])
                self.bin_edges = 10**log10_bin_boundaries - 1 + self.values[0]
                self.counts = {v:np.zeros(2) for v in range(1,self.bins+1)}
            else:
                raise NotImplementedError("Not supported bin_edge_type. Choose from 'linear' or 'log'.")
        else:
            raise NotImplementedError("Not supported var_type. Choose from 'discrete' or 'continuous'.")

    def _apply_prior(self):
        if self.prior == "uniform":
            if self.type == "discrete":
                self.counts = {v:np.ones(2) for v in self.values}
                self.prior = {v:np.ones(2) for v in self.values} #replace the prior string with the actual numerical values for the prior
            elif self.type == "continuous":
                self.counts = {v:np.ones(2) for v in range(1,self.bins+1)}   #use one-based indexing in compliance with np.digitize
                self.prior = {v:np.ones(2) for v in range(1,self.bins+1)} 
        else:
            #so far only a uniform prior is supported, but any arbitrary prior can be easily added here
            raise NotImplementedError
    
    def _dict_argmax(self,d): #function that computes the argmax of dictionary if the values for each key are scalars, returns the key of the maximum value in the dictionary
        arr = np.array(list(d.values()))
        max_idx = np.nanargmax(arr)
        max_key = list(d.keys())[max_idx]

        return max_key

    def update_counts(self,result,variable_value):  #result needs to be 0 or 1 where 0 is a fail (no collision for scenario variables or FP/FN/over budget for fidelity settings) and 1 is a success (collision for scenario variables or TP/TN for fidelity settings).
        if self.type == "discrete":
            if variable_value not in self.values:
                raise NotImplementedError("The discrete variable value is not in the specified range. Variable value: {}, possible values: {}".format(variable_value,self.values))
            else:
                self.counts[variable_value][result] += 1
        if self.type == "continuous":
            bin = np.digitize(variable_value,self.bin_edges)   #one  based bin
            if bin == 0 or bin>self.bins:
                bin = np.digitize(variable_value,self.bin_edges,right=True) #check if on upper bound
                if bin<=self.bins:
                    self.counts[bin][result] += 1
                else:
                    raise NotImplementedError("The continuous variable value is not in the specified range. Variable value : {}, bin edges: {}".format(variable_value,self.bin_edges))
            else:
                self.counts[bin][result] += 1
    
    def sample_theta(self):   #function that samples values theta from each "arm", i.e., constructs the Dirichlet distribution for each value/bin and samples from it, returns a dictionary with the same keys as self.counts and the sampled value.
        sampled_theta = {}
        for k in self.counts.keys():
            dist = torch.distributions.beta.Beta(self.counts[k][1],self.counts[k][0])   #need to reverse the order as the alpha parameters in a beta distribution is the counts of success which we defined as index 1 and index 0 is the index for failure
            sampled_theta[k] = dist.sample().item()
        return sampled_theta
    
    def sample_thompson(self):  #function that applies thompson sampling to recommond the next configuration to try out. In case of self.type=="discrete" returns the string of the samples class as specified in self.values, if self.type=="continuous", a numerical value that sampled from a uniform distribution within the selected bin is returned.
        sampled_theta = self.sample_theta()
        max_class = self._dict_argmax(sampled_theta)
        if self.type == "discrete":
            return max_class
        
        elif self.type == "continuous":
            #get bins edges and sample continuous value from uniform/logarithmically between bin edges (depends on self.bin_edge_type)
            bin_lower_edge = self.bin_edges[max_class - 1]
            bin_upper_edge = self.bin_edges[max_class]
            
            #case of linear conitinuous variable
            if self.bin_edge_type == "linear":
                uniform_dist = torch.distributions.uniform.Uniform(bin_lower_edge,bin_upper_edge)
                sampled_value = uniform_dist.sample().item()
                return sampled_value
            
            #case log-scaled continuous variable
            elif self.bin_edge_type == "log":
                transformed_lower_bound = 1 #set arbitrary to positive number
                transformed_upper_bound = transformed_lower_bound + (bin_upper_edge - bin_lower_edge)
                log_lower_bound = np.log10(transformed_lower_bound)
                log_upper_bound = np.log10(transformed_upper_bound)
                samples_log_space = torch.distributions.uniform.Uniform(log_lower_bound,log_upper_bound).sample().item()
                samples_normalized_space = 10**samples_log_space
                sampled_value = (samples_normalized_space-10**log_lower_bound)*(bin_upper_edge-bin_lower_edge)/(10**log_upper_bound - 10**log_lower_bound)+ bin_lower_edge
                if (sampled_value >= bin_lower_edge) and (sampled_value <= bin_upper_edge):
                    return sampled_value
                else:
                    raise ValueError("The sampled value is not within the specified bin edges.")
    
    def _mode(self):  #function that returns the mode for the beta distribution of each individual arm as a dictionary with the same keys as self.counts
        mode_theta = {}
        for k in self.counts.keys():
            dist = torch.distributions.beta.Beta(self.counts[k][1],self.counts[k][0])   #need to reverse the order as the alpha parameters in a beta distribution is the counts of success which we defined as index 1 and index 0 is the index for failure
            mode_theta[k] = dist.mode.item()
        return mode_theta
    
    def get_map(self):  #returns the key of the variable with largest mode
        modes = self._mode()
        argmax_mode = self._dict_argmax(modes)
        
        #discrete case
        if self.type == "discrete":
            return argmax_mode

        #continuous case
        elif self.type == "continuous":
            if self.bin_edge_type == "linear":
                lower_edge = self.bin_edges[argmax_mode-1]
                upper_edge = self.bin_edges[argmax_mode]
                return (lower_edge + upper_edge) /2
            
            elif self.bin_edge_type == "log":
                lower_edge = self.bin_edges[argmax_mode-1]
                upper_edge = self.bin_edges[argmax_mode]

                mean_value = 1/(np.log10(1+upper_edge-lower_edge)*np.log(10))*(upper_edge-lower_edge+(lower_edge-1)*np.log(1-lower_edge+upper_edge))
                return mean_value
            else:
                raise NotImplementedError("Only linear and logarithmic bin_edge_types are supported yet.")
        else:
            raise NotImplementedError("Currently only 'discrete' and 'continuous' variables are supported")

        
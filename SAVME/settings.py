from SAVME.variable import Variable

class Settings(object):
    def __init__(self,variables_config) -> None:   #variables is a dict of form {name:{"var_type":var_type,"values":values,"bins":bins,"bin_edge_type":bin_edge_type,"prior":prior}}
        self.variables = {}
        for name in variables_config.keys():
            self.variables[name] = Variable(name,**variables_config[name])

    def sample_from_prior(self):    #Thompson sampling from prior for each of the variables returns a dictionary with keys of self.variables with sampled values
        sampled_values = {name:self.variables[name].sample_thompson() for name in self.variables.keys()}
        
        return sampled_values
        
    def update_prior(self,result,variable_values):  # result is either 0 or 1 where 0 is a fail (no collision for scenario variables or FP/FN/over budget for fidelity settings) and 1 is a success (collision for scenario variables or TP/TN for fidelity settings). Variable values is a dictionary of the same format as returned by self.sample_from_prior.
        for name in self.variables.keys():
            self.variables[name].update_counts(result,variable_values[name])
    
    def get_map(self): #returns the MAP estimate for all variables. Choosing the MAP estimate is greedy (pure exploitation) and should only be the last step when determining best settings after learning.
        map_values = {name:self.variables[name].get_map() for name in self.variables.keys()}

        return map_values
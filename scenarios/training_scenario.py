import numpy as np

class TrainingScenario(object):

    def get_constraints(self):
        constraints = {"THETA_INIT":{"var_type":"continuous","values":(0,np.pi),"bins":10,"bin_edge_type":"linear"},   #training scenarios have initial conditions for theta from 0 to pi
                       "THETA_DOT_INIT": {"var_type":"continuous", "values":(-1, 1),"bins":10,"bin_edge_type":"linear"}}
        return constraints








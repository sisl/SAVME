import numpy as np

class TestingScenario(object):

    def get_constraints(self):
        constraints = {"THETA_INIT":{"var_type":"continuous","values":(-np.pi,0),"bins":10,"bin_edge_type":"linear"},   #testing scenarios have initial conditions for theta from -pi to p0
                       "THETA_DOT_INIT": {"var_type":"continuous", "values":(-1, 1),"bins":10,"bin_edge_type":"linear"}}
        return constraints








import yaml
from scenarios.utils import *
from SAVEM.simulator_interface import ADP_DIRECTORY

"""
Variable List:
var 1 init velocity
var 2 min dist
var 3 distance (behavior)
var 4 deceleration
var 5 utm x
var 6 speed
"""

yaml_blp = """
spectral:
  enable: true
  environment:
    weather: {VAR0}
metadata:
  name: cv_stop
  scenario_version: v0.96
  description: ''
  author_email: nboord@stanford.edu
sim_end:
  route_end: true # will also end the simulation if ego hits the destination point
  until:
  - timeout:
      secs: 15s
include:
- file: scenario://workspace/{CONFIG_FILE}
map:
  key: straight_flat_bidirectional_5km
projection_settings:
  utm:
    north: true
    zone: 10
vehicle:
  mesh_name: applied:car
  shape:
    back_edge_to_center: 1.072
    front_edge_to_center: 3.8
    height: 1.478
    left_edge_to_center: 0.926
    right_edge_to_center: 0.926
  kinematic_bicycle:
    wheelbase: 2.86
    max_velocity: 60
    max_deceleration: 8.0
    max_acceleration: 3.0
    max_steering_angle: 0.52
    max_steering_rate: 0.84
    num_integration_steps: 1
agents:
- ego:
    initial_position:
      point:
        utm:
          x: 500023.7928481
          y: 4499996
      heading: 0
    initial_velocity_mps: {VAR1}
    behaviors:
    - smooth_lane_keeping:
        # adaptive_cruise:
        #   desired_time_gap: 5s
        #   min_dist: 5
        #   max_accel: 3
        #   max_decel: 3
        #   enforce_max_bounds: true
        params:
          distance: 200
        constant_velocity:
- obstacle: # front car
    behaviors:
    - smooth_lane_keeping:
        adaptive_cruise:
          desired_time_gap: 5s
          min_dist: {VAR2}
          max_accel: 3
          max_decel: 3
          enforce_max_bounds: true
        params:
          distance: {VAR3}
        constant_velocity:
    - stop:
        deceleration: {VAR4}
    model:
      static:
        height: 1.5
        point:
        - x: 2.3
          y: 0.9
        - x: 2.3
          y: -0.9
        - x: -2.3
          y: -0.9
        - x: -2.3
          y: 0.9
    initial_state:
      point:
        utm:
            x: {VAR5}
            y: 4499996
            z: 0
      speed_mps: {VAR6}
      heading: 0
    type: VEHICLE
    id: 1
trip_agent:
  behavior:
  - generate_route:
      start:
        utm:
          x: 500023.7928481
          y: 4499996
      dest:
        utm:
          x: 500203.36051197787
          y: 4499996
"""


class CVStopScenario:
    # def get_constraints(self):
    #     constraints = {"VAR0":["choice",weather_choices],"VAR1": ["range", (11.5, 25)], "VAR2": ["range", (0.5, 6.5)], "VAR3": ["range", (45, 65)],
    #                    "VAR4": ["range", (3, 7)], "VAR5": ["range", (500057, 500072)], "VAR6": ["range", (10, 25)]}
    #     return constraints
    def get_constraints(self):
        constraints = {"VAR0":{"var_type":"discrete","values":weather_choices},
                       "VAR1": {"var_type":"continuous", "values":(11.5, 25)}, 
                       "VAR2": {"var_type":"continuous", "values":(0.5, 6.5)}, 
                       "VAR3": {"var_type":"continuous", "values":(45, 65)},
                       "VAR4": {"var_type":"continuous", "values":(3, 7)}, 
                       "VAR5": {"var_type":"continuous", "values":(500057, 500072)}, 
                       "VAR6": {"var_type":"continuous", "values":(10, 25)}}
        return constraints

    def get_yaml(self, scenario_settings, fidelity_settings,file_root):
        filename_main = file_root+"_main.scn.yaml"
        filename_config = file_root+"_config.inc.yaml"
        
        fidelity_yaml = yaml.safe_load(fidelity_blueprint.format(**fidelity_settings))  # add final fidelity string to YAML
        scenario_settings["CONFIG_FILE"] = filename_config
        main_yaml = yaml.safe_load(yaml_blp.format(**scenario_settings))
        write_to_yaml(ADP_DIRECTORY+"scenarios/"+filename_main, main_yaml)
        write_to_yaml(ADP_DIRECTORY+"scenarios/"+filename_config, fidelity_yaml)

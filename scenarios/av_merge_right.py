import yaml
import random
from scenarios.utils import *
from SAVEM.simulator_interface import ADP_DIRECTORY

"""
Variable List:
var 1 initial position ego (x,y,heading)
var 2 init velocity ego mps 
var 3 initial position obstacle (x,y,heading)
var 4 initial velocity obstacle mps
"""

yaml_blp = """
spectral:
  enable: true
  environment:
    weather: {VAR0}
metadata:
  name: merge_scenario
  scenario_version: v0.96
  description: ''
  author_email: mschl@stanford.edu
sim_end:
  route_end: true
  until:
  - timeout:
      secs: 15s
include:
- file: scenario://workspace/{CONFIG_FILE}
map:
  key: sunnyvale
projection_settings:
  utm:
    north: true
    zone: 10
vehicle:
  mesh_name: applied:car
  shape:
    back_edge_to_center: 0.7
    front_edge_to_center: 3.5
    height: 1.6
    left_edge_to_center: 0.9
    right_edge_to_center: 0.9
  kinematic_bicycle:
    wheelbase: 2.6
    max_velocity: 50
    max_deceleration: 8.0
    max_acceleration: 2.5
    max_steering_angle: 0.52
    max_steering_rate: 0.84
    num_integration_steps: 1
agents:
- ego:
    initial_position:
      point:
        utm:
          x: {VAR1[0]}
          y: {VAR1[1]}
      heading: {VAR1[2]}
    initial_velocity_mps: {VAR2}
    behaviors:
    - smooth_lane_keeping:
        params:
          distance: 100
        constant_velocity:
- obstacle:
    behaviors:
    - smooth_lane_keeping:
        params:
          distance: 100
        constant_velocity:
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
    motion_model:
      external: {{}}
    initial_state:
      point:
        utm:
          x: {VAR3[0]}
          y: {VAR3[1]}
          z: 0
      speed_mps: {VAR4}
      heading: {VAR3[2]}
    type: VEHICLE
    id: 1
trip_agent:
  behavior:
  - generate_route:
      start:
        utm:
          x: {VAR1[0]}
          y: {VAR1[1]}
      dest:
        utm:
          x: 587496.631175419
          y: 4140726.0272290804
          z: 0

"""

class AVMergeRightScenario:
    # def get_constraints(self):
    #     constraints = {"VAR0":["choice",weather_choices],"VAR1": ["range", (163, 185)], "VAR2": ["range", (10, 17)], "VAR3": ["range", (0.5, 5.5)],
    #                    "VAR4": ["range", (109, 132)], "VAR5": ["range", (11.5, 20)]}
    #     return constraints
    def get_constraints(self):
        constraints = {"VAR0":{"var_type":"discrete","values":weather_choices},
                       "VAR1": {"var_type":"discrete", "values":[(587531.93,4140722.75,-2.128),(587527.30,4140715.52,-2.448),(587522.70,4140712.85,-2.897)]}, 
                       "VAR2": {"var_type":"continuous", "values":(5,15)}, 
                       "VAR3": {"var_type":"discrete", "values":[(587519.58,4140695.75,2.1822),(587514.81,4140701.97,2.246),(587510.69,4140707.44,2.190)]},
                       "VAR4": {"var_type":"continuous", "values":(5,15)}
                       }
        return constraints


    def get_yaml(self, scenario_settings, fidelity_settings,file_root):
        filename_main = file_root+"_main.scn.yaml"
        filename_config = file_root+"_config.inc.yaml"
        
        fidelity_yaml = yaml.safe_load(fidelity_blueprint.format(**fidelity_settings))  # add final fidelity string to YAML
        scenario_settings["CONFIG_FILE"] = filename_config
        main_yaml = yaml.safe_load(yaml_blp.format(**scenario_settings))
        write_to_yaml(ADP_DIRECTORY+"scenarios/"+filename_main, main_yaml)
        write_to_yaml(ADP_DIRECTORY+"scenarios/"+filename_config, fidelity_yaml)


import yaml
import random
from scenarios.utils import *
from SAVEM.simulator_interface import ADP_DIRECTORY

"""
Variable List:
var 1 x init position ego
var 2 init velocity mps 
var 3 min dist
var 4 utm y
var 5 speed mps
"""


yaml_blp = """
spectral:
  enable: true
  environment:
    weather: {VAR0}
metadata:
  name: av_left_cv_straight_same_direction
  scenario_version: v0.96
  description: ''
  author_email: nboord@stanford.edu
sim_end:
  route_end: true
  until:
  - timeout:
      secs: 20s
include:
- file: scenario://workspace/{CONFIG_FILE}
map:
  key: ideal_intersection
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
    max_velocity: 30
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
          x: {VAR1}
          y: 100
      heading: 0
    initial_velocity_mps: {VAR2}
    behaviors:
    - path_following:
        pose_b_spline:
          default_tangent_distance: 0.5
          poses:
          - x: 194.23788579339532
            y: 100
            heading: 0.025
          - x: 203.4644384444432
            y: 100.60159504406782
            heading: 0.266
          - x: 209.0895333287133
            y: 104.05168193065897
            heading: 0.787
          - x: 212.2714229471499
            y: 109.43152934930207
            heading: 1.367
          - x: 213.25000000005335
            y: 128.07927034068373
            heading: 1.5719516248246708
            tangent_distance: 8.16009030878011
        constant_velocity:
- obstacle:
    behaviors:
    - smooth_lane_keeping:
        adaptive_cruise:
          desired_time_gap: 5s
          min_dist: {VAR3}
          max_accel: 3
          max_decel: 3
          enforce_max_bounds: true
        params:
          distance: 200
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
    initial_state:
      point:
        utm:
          x: 213.25000000037647
          y: {VAR4}
          z: 0
      speed_mps: {VAR5}
      heading: 1.570796326790008
    type: VEHICLE
    id: 1
trip_agent:
  behavior:
  - generate_route:
      start: {{utm: {{x: 180, y: 100}} }}
      dest: {{utm: {{x: 213, y: 124}} }}
      interpolation_distance: 0.5
"""

class AVLeftCVStraightSameDirectionScenario:
    # def get_constraints(self):
    #     constraints = {"VAR0":["choice",weather_choices],"VAR1": ["range", (166, 184)], "VAR2": ["range", (10, 18)], "VAR3": ["range", (1.5, 6.5)],
    #                    "VAR4": ["range", (69, 76)], "VAR5": ["range", (11, 20)]}
    #     return constraints
    def get_constraints(self):
        constraints = {"VAR0":{"var_type":"discrete","values":weather_choices},
                       "VAR1": {"var_type":"continuous", "values":(166, 184)}, 
                       "VAR2": {"var_type":"continuous", "values":(10, 18)}, 
                       "VAR3": {"var_type":"continuous", "values":(1.5, 6.5)},
                       "VAR4": {"var_type":"continuous", "values":(69, 76)}, 
                       "VAR5": {"var_type":"continuous", "values":(11, 20)}}
        return constraints


    def get_yaml(self, scenario_settings, fidelity_settings,file_root):
        filename_main = file_root+"_main.scn.yaml"
        filename_config = file_root+"_config.inc.yaml"
        
        fidelity_yaml = yaml.safe_load(fidelity_blueprint.format(**fidelity_settings))  # add final fidelity string to YAML
        scenario_settings["CONFIG_FILE"] = filename_config
        main_yaml = yaml.safe_load(yaml_blp.format(**scenario_settings))
        write_to_yaml(ADP_DIRECTORY+"scenarios/"+filename_main, main_yaml)
        write_to_yaml(ADP_DIRECTORY+"scenarios/"+filename_config, fidelity_yaml)


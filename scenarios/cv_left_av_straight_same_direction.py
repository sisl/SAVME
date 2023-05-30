import yaml
import random
from scenarios.utils import *
from SAVEM.simulator_interface import ADP_DIRECTORY


yaml_blp = """
spectral:
  enable: true
  environment:
    weather: {VAR0}
metadata:
  name: cv_left_av_straight_same_direction
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
    back_edge_to_center: 0.7
    front_edge_to_center: 3.5
    height: 1.6
    left_edge_to_center: 0.9
    right_edge_to_center: 0.9
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
          x: 213.2500000003153
          y: {VAR1}
          z: 0
      heading: 1.570796326790008
    initial_velocity_mps: {VAR2}
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
- obstacle:
    behaviors:
    - path_following:
        pose_b_spline:
          default_tangent_distance: 3
          poses:
          - x: 185.89400916539074
            y: 100
            heading: 0
          - x: 199.86302576196252
            y: 100
            heading: 0.176
          - x: 209.1827760817945
            y: 104.15217371882503
            heading: 0.711
          - x: 212.66153724378273
            y: 111.02621209377993
            heading: 1.364
          - x: 213.2500000000503
            y: 138.79245455755128
            heading: 1.524
        adaptive_cruise:
          desired_time_gap: 5s
          min_dist: {VAR3}
          max_accel: {VAR4}
          max_decel: {VAR5}
          enforce_max_bounds: true
        motion_profile:
          phases:
          - ramp_velocity:
              distance: {VAR6}
              target: {VAR7}
          - hold_velocity:
              distance: 50
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
          x: {VAR8}
          y: 100
          z: 0.01300000000000523
      speed_mps: {VAR9}
      heading: 0
    type: VEHICLE
    id: 1
trip_agent:
  behavior:
  - generate_route:
      start:
        utm:
          x: 213.2500000003153
          y: 64.75287689828743
          z: 0
      dest:
        utm:
          x: 213.2500000001454
          y: 142.99435625932864
"""

class CVLeftAVStraightSameDirectionScenario:
    # def get_constraints(self):
    #     constraints = {"VAR0":["choice",weather_choices],"VAR1": ["range", (53, 90)], "VAR2": ["range", (13, 20)], "VAR3": ["range", (0.5, 5.5)],
    #                    "VAR4": ["range", (2, 7)], "VAR5": ["range", (4, 7)],
    #                    "VAR6": ["range", (25, 75)], "VAR7": ["range", (10, 20)],
    #                    "VAR8": ["range", (153, 184)], "VAR9": ["range", (10, 20)]}
    #     return constraints
    def get_constraints(self):
        constraints = {"VAR0":{"var_type":"discrete","values":weather_choices},
                       "VAR1": {"var_type":"continuous", "values":(53, 90)}, 
                       "VAR2": {"var_type":"continuous", "values":(13, 20)}, 
                       "VAR3": {"var_type":"continuous", "values":(0.5, 5.5)},
                       "VAR4": {"var_type":"continuous", "values":(2, 7)}, 
                       "VAR5": {"var_type":"continuous", "values":(4, 7)},
                       "VAR6": {"var_type":"continuous", "values":(25, 75)}, 
                       "VAR7": {"var_type":"continuous", "values":(10, 20)},
                       "VAR8": {"var_type":"continuous", "values":(153, 184)}, 
                       "VAR9": {"var_type":"continuous", "values":(10, 20)}}
        return constraints


    def get_yaml(self, scenario_settings, fidelity_settings,file_root):
        filename_main = file_root+"_main.scn.yaml"
        filename_config = file_root+"_config.inc.yaml"
        
        fidelity_yaml = yaml.safe_load(fidelity_blueprint.format(**fidelity_settings))  # add final fidelity string to YAML
        scenario_settings["CONFIG_FILE"] = filename_config
        main_yaml = yaml.safe_load(yaml_blp.format(**scenario_settings))
        write_to_yaml(ADP_DIRECTORY+"scenarios/"+filename_main, main_yaml)
        write_to_yaml(ADP_DIRECTORY+"scenarios/"+filename_config, fidelity_yaml)


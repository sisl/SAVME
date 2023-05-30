import yaml
from scenarios.utils import *
from SAVEM.simulator_interface import ADP_DIRECTORY

"""
Variable List:
var 1 init velocity
var 2 min dist
var 3 max accel
var 4 max decel
var 5 hold velocity distance
var 6 ramp velocity distance
var 7 ramp vel target
var 8 transition dist
var 9 lane follow dist
var 11 utm x
var 12 speed
"""

yaml_blp = """
spectral:
  enable: true
  environment:
    weather: {VAR0}
metadata:
  name: av_cut_in
  scenario_version: v0.96
  description: ''
  author_email: nboord@stanford.edu
sim_end:
  route_end: true # will also end the simulation if ego hits the destination point
  until:
  - timeout:
      secs: 20s
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
          x: 500030.9618450611
          y: 4499992
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
          distance: 150
        motion_profile:
          phases:
          - hold_velocity:
              distance: 150
- obstacle:
    behaviors:
    - smooth_lane_keeping:
        adaptive_cruise:
          desired_time_gap: 5s
          min_dist: {VAR2}
          max_accel: {VAR3}
          max_decel: {VAR4}
          enforce_max_bounds: true
        params:
          distance: 150
        motion_profile:
          phases:
          - hold_velocity:
              distance: {VAR5}
          - ramp_velocity:
              distance: {VAR6}
              target: {VAR7}
          - hold_velocity:
              distance: 50
      until:
        timeout:
          secs: 3s
    - lane_change:
        adaptive_cruise:
          desired_time_gap: 5s
          min_dist: 5
          max_accel: 3
          max_decel: 3
          enforce_max_bounds: true
        relative_lane:
          change_direction: RIGHT
          num_lanes: 1
          transition_distance: {VAR8}
          lane_follow_distance: {VAR9}
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
            x: {VAR10}
            y: 4499996
            z: 0
      speed_mps: {VAR11}
      heading: 0
    type: VEHICLE
    id: 1
trip_agent:
  behavior:
  - generate_route:
      start:
        utm:
          x: 500030.9618450611
          y: 4499992
      dest:
        utm:
          x: 500154.95721019263
          y: 4499992
"""
class CVCutInScenario:
    # def get_constraints(self):
    #     constraints = {"VAR0":["choice",weather_choices],"VAR1": ["range", (16, 18)], "VAR2": ["range", (0.5, 6.5)], "VAR3": ["range", (2, 8)],
    #                    "VAR4": ["range", (2, 8)], "VAR5": ["range", (15, 20.5)],
    #                    "VAR6": ["range", (32, 75)], "VAR7": ["range", (10, 20)],
    #                    "VAR8": ["range", (15, 40)], "VAR9": ["range", (20, 45)],
    #                    "VAR10": ["range", (500041, 500061)],
    #                    "VAR11": ["range", (10, 20)]}
    #     return constraints
    def get_constraints(self):
        constraints = {"VAR0":{"var_type":"discrete","values":weather_choices},
                       "VAR1": {"var_type":"continuous", "values":(16, 18)}, 
                       "VAR2": {"var_type":"continuous", "values":(0.5, 6.5)}, 
                       "VAR3": {"var_type":"continuous", "values":(2, 8)},
                       "VAR4": {"var_type":"continuous", "values":(2, 8)}, 
                       "VAR5": {"var_type":"continuous", "values":(15, 20.5)},
                       "VAR6": {"var_type":"continuous", "values":(32, 75)}, 
                       "VAR7": {"var_type":"continuous", "values":(10, 20)},
                       "VAR8": {"var_type":"continuous", "values":(15, 40)}, 
                       "VAR9": {"var_type":"continuous", "values":(20, 45)},
                       "VAR10": {"var_type":"continuous", "values": (500041, 500061)},
                       "VAR11": {"var_type":"continuous", "values": (10, 20)}}
        return constraints

    def get_yaml(self, scenario_settings, fidelity_settings,file_root):
        filename_main = file_root+"_main.scn.yaml"
        filename_config = file_root+"_config.inc.yaml"
        
        fidelity_yaml = yaml.safe_load(fidelity_blueprint.format(**fidelity_settings))  # add final fidelity string to YAML
        scenario_settings["CONFIG_FILE"] = filename_config
        main_yaml = yaml.safe_load(yaml_blp.format(**scenario_settings))
        write_to_yaml(ADP_DIRECTORY+"scenarios/"+filename_main, main_yaml)
        write_to_yaml(ADP_DIRECTORY+"scenarios/"+filename_config, fidelity_yaml)



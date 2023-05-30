import yaml
import random
from scenarios.utils import *
from SAVEM.simulator_interface import ADP_DIRECTORY

"""
Variable List:
var 1 init y
var 2 init vel
var 3 min dist
var 4 speed
"""


yaml_blp = """
spectral:
  enable: true
  environment:
    weather: {VAR0}
metadata:
  name: parking_lot_backup
  scenario_version: v0.96
  description: ''
  author_email: nboord@stanford.edu
sim_end:
  route_end: true
  until:
  - timeout:
      secs: 6s
include:
- file: scenario://workspace/simian_examples/include/vehicle_shape.inc.yaml
- file: scenario://workspace/{CONFIG_FILE}
map:
  key: parking_lot
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
          x: 596969.0833639127
          y: {VAR1}
          z: 0.01300000000000523
      heading: -1.4552542905093273
    initial_velocity_mps: {VAR2}
    behaviors:
    - path_following:
        # adaptive_cruise:
        #   desired_time_gap: 5s
        #   min_dist: 5
        #   max_accel: 3
        #   max_decel: 3
        #   enforce_max_bounds: true
        pose_b_spline:
          default_tangent_distance: 0.5
          poses:
          - x: 596970.7074617672
            y: 4133126.0536609483
            heading: -1.444
          - x: 596970.7074617672
            y: 4133126.0536609483
            heading: -1.449
          - x: 596975.8153905757
            y: 4133084.4605263663
            heading: -1.449
          - x: 596975.8153905757
            y: 4133084.4605263663
            heading: 0
        motion_profile:
          phases:
          - hold_velocity:
              distance: 100
- obstacle:
    behaviors:
    - path_following:
        adaptive_cruise:
          desired_time_gap: 5s
          min_dist: {VAR3}
          max_accel: 3
          max_decel: 3
          enforce_max_bounds: true
        pose_b_spline:
          default_tangent_distance: 3
          poses:
          - x: 596975.677124544
            y: 4133110.810787296
            heading: 2.576
          - x: 596972.5430496703
            y: 4133116.3802605225
            heading: 1.698
        constant_velocity:
    - path_following:
        pose_b_spline:
          default_tangent_distance: 3
          poses:
          - x: 596970.3264725363
            y: 4133114.615884935
            heading: -1.592
          - x: 596972.1744113838
            y: 4133098.824407511
            heading: -1.449
          - x: 596975.8702890789
            y: 4133069.2573859505
            heading: -1.446
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
          x: 596980.3455718497
          y: 4133111.4478415344
          z: 0
      speed_mps: {VAR4}
      heading: 0.10757577291093906
    type: VEHICLE
    id: 1
trip_agent:
  behavior:
  - generate_route:
      start:
        utm:
          x: 596969.0833639127
          y: 4133138.8367830114
      dest:
        utm:
          x: 596973.6640487115
          y: 4133101.294690734
"""

class ParkingLotBackupScenario:
    # def get_constraints(self):
    #     constraints = {"VAR0":["choice",weather_choices],"VAR1": ["range", (41331139, 4133151)], "VAR2": ["range", (5, 6)], "VAR3": ["range", (0.5, 4.5)],
    #                    "VAR4": ["range", (1, 3)]}
    #     return constraints

    def get_constraints(self):
        constraints = {"VAR0":{"var_type":"discrete","values":weather_choices},
                       "VAR1": {"var_type":"continuous", "values":(4133139, 4133151)}, 
                       "VAR2": {"var_type":"continuous", "values":(5, 6)}, 
                       "VAR3": {"var_type":"continuous", "values":(0.5, 4.5)},
                       "VAR4": {"var_type":"continuous", "values":(1, 3)}}
        return constraints


    def get_yaml(self, scenario_settings, fidelity_settings,file_root):
        filename_main = file_root+"_main.scn.yaml"
        filename_config = file_root+"_config.inc.yaml"
        
        fidelity_yaml = yaml.safe_load(fidelity_blueprint.format(**fidelity_settings))  # add final fidelity string to YAML
        scenario_settings["CONFIG_FILE"] = filename_config
        main_yaml = yaml.safe_load(yaml_blp.format(**scenario_settings))
        write_to_yaml(ADP_DIRECTORY+"scenarios/"+filename_main, main_yaml)
        write_to_yaml(ADP_DIRECTORY+"scenarios/"+filename_config, fidelity_yaml)


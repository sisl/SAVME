import random
import yaml

#list of all weather conditions in Spectral
weather_choices = ["NIGHT", "CLEARNOON","CLOUDYNOON","WETNOON","WETCLOUDYNOON","MIDRAINNOON","HARDRAINNOON","SOFTRAINNOON","CLEARSUNSET",
                   "CLOUDYSUNSET","WETSUNSET","WETCLOUDYSUNSET","MIDRAINSUNSET","HARDRAINSUNSET","SOFTRAINSUNSET","SNOWCLEARNOON","SNOWCLOUDYNOON"]
# weather_choices = ["CLEARNOON","CLOUDYNOON","WETNOON","WETCLOUDYNOON","MIDRAINNOON","HARDRAINNOON","SOFTRAINNOON",
                  #  "SNOWCLEARNOON","SNOWCLOUDYNOON"]

fidelity_constraints = {"camera_view_distance":["range",(0,3),lambda k:5*10**k],    #need to calculate the actual viewing distance as 5*10^k
                        "camera_bloom_level":["choice",("HIGH","LOW"),lambda x:x],
                        "camera_bloom_disable":["choice",("true","false"),lambda x:x],
                        "camera_disable_lighting":["choice",("true","false"),lambda x:x],
                        "camera_disable_shadows":["choice",("true","false"),lambda x:x],
                        "camera_disable_models":["choice",("true","false"),lambda x:x],   #fog, lens, etc.
                        "camera_disable_depth_of_field":["choice",("true","false"),lambda x:x],
                        "camera_near_clipping_distance":["range",(-1,1),lambda k:2*10**k],  #need to calculate the actual near clipping distance as 2*10^k
                        "camera_disable_shot_noise":["choice",("true","false"),lambda x:x],
                        "lidar_disable_shot_noise":["choice",("true","false"),lambda x:x],
                        "lidar_enable_ambient":["choice",("true","false"),lambda x:x],
                        "lidar_disable_translucency":["choice",("true","false"),lambda x:x],
                        "lidar_subsample_count":["choice",(1,2,3,4,5),lambda x:x],
                        "lidar_near_clipping_distance":["range",(-1,1),lambda k:2*10**k],  #need to calculate the actual near clipping distance as 2*10^k
                        "lidar_raytracing_bounces":["choice",(0,1,2,3,4),lambda x:x],
                        "FREQUENCY":["choice",(10,),lambda x:x]    #for now there is only one option for the frequency until we have determinedS
                        }

high_fidelity_settings = {"camera_view_distance":5000,    #need to calculate the actual viewing distance as 5*10^k
                          "camera_bloom_level":"HIGH",
                          "camera_bloom_disable":"false",
                          "camera_disable_lighting":"false",
                          "camera_disable_shadows":"false",
                          "camera_disable_models":"false",   #fog, lens, etc.
                          "camera_disable_depth_of_field":"false",
                          "camera_near_clipping_distance":0.2,  #need to calculate the actual near clipping distance as 2*10^k
                          "camera_disable_shot_noise":"false",
                          "lidar_disable_shot_noise":"false",
                          "lidar_enable_ambient":"true",
                          "lidar_disable_translucency":"false",
                          "lidar_subsample_count":5,
                          "lidar_near_clipping_distance":0.2,  #need to calculate the actual near clipping distance as 2*10^k
                          "lidar_raytracing_bounces":4,
                          "FREQUENCY":10    #for now there is only one option for the frequency until we have determinedS
                          }

fidelity_blueprint = """
vehicle:
  sensors:
    sensor_models:
# --------------------CAMERA 1------------------------------------------------
    - camera_model:
        fidelity:
          view_distance: {camera_view_distance}
          bloom:
            level: {camera_bloom_level}
            disable: {camera_bloom_disable}
          disable_lighting: {camera_disable_lighting}
          disable_shadows: {camera_disable_shadows}
          disable_models: {camera_disable_models}
          disable_depth_of_field: {camera_disable_depth_of_field}
          near_clipping_distance: {camera_near_clipping_distance}
          disable_shot_noise: {camera_disable_shot_noise}
          cubemap_filtered_sampling: true
          super_sampling: 1
        format:
          data: PROTO_MSG
          save_directory: /tmp/spectral
        library:
          model: realistic
          vendor: applied
        standard_params:
          field_of_view:
            az: 1.5705
          frame_rate: 27
          lens_params:
            affine_scaling:
            - 1
            - 0
            - 0
            - 1
            center_position: {{}}
            chromatic_aberration: 0.02
            cropping: 1
            f_number: 1.8
            focal_length: 10
            lens_flare: 0.001
            library: {{}}
            projection: RECTILINEAR
            spot_size: 0.005
            tangential_distortion:
            - 0
            - 0
            vignetting:
              alpha: 3.25
              intensity: 2
              radius: 1
          sensor_params:
            bloom: 1
            color_depth: 8
            color_filter_array:
              demosaic: BILINEAR
              layout:
                P1: G
                P2: R
                P3: B
                P4: G
              transmittance:
                P1: 0.87
                P2: 0.9
                P3: 0.9
                P4: 0.87
            dynamic_range: 96
            fixed_pattern_noise:
              dsnu: 0.001
              prnu: 0.005
            full_well_capacity: 2923648
            iso: 100
            library: {{}}
            pixel_size:
              x: 10.4166666667
              y: 10.4166666667
            quantum_effeciency: 0.95
            readout_noise: 0.01
            resolution:
              x: 1920
              y: 960
            shutter_speed: 6000
            size:
              x: 20
              y: 11.25
            technology: CMOS
            type: VISIBLE
          shroud_params:
            dirt: {{}}
            fog: {{}}
            rain: {{}}
          system_params:
            color_space: RGB
            depth_params:
              log_base: 300
              max: 1000
              type: LOG
            exposure:
              auto_exposure: true
              dynamic_range:
                max: 20
                min: -2
              speed: 50
            gain: 1
            gamma: 0.4545
            saturation:
              a: 0.65
              b: 0.65
              g: 0.65
              r: 0.65
            time_of_flight_params:
              detector_params:
                bandwidth: 5000000
                dynamic_range: 50
                lens_area: 0.00282743338
                minimum_snr: 10
                noise_floor: -120
                precision:
                  max: 0.01
                  min: 0.001
                saturation_limit: -85
              emitter_params:
                center_wavelength: 850
                exposure_time: 0.001
                optical_passband:
                  max: 860
                  min: 840
                peak_power: 7
            white_balance: -1
        name: camera_0
        mount:
          px: 1.5
          py: 0
          pz: 2.2
          rpy:
            roll: 0
            pitch: 0
            yaw: 0
# --------------------LIDAR 1------------------------------------------------
    - lidar_model:
        library:
          vendor: velodyne
          model: ultra_puck
        name: lidar_0
        fidelity:
          disable_shot_noise: {lidar_disable_shot_noise}
          enable_ambient: {lidar_enable_ambient}
          disable_translucency: {lidar_disable_translucency}
          subsample_count: {lidar_subsample_count}
          near_clipping_distance: {lidar_near_clipping_distance}
          raytracing:
            bounces: {lidar_raytracing_bounces}
        mount:
          px: 1.5
          py: 0.0
          pz: 2.2
          rpy:
            roll: 0.0
            pitch: 0.0
            yaw: 0.0
        standard_params:
          frame_rate: 20.0
          detector_params:
            range: {{min: 0, max: 90}}
        format:
          data: ROS_TOPIC
          semantic_segmentation: true
          intensity:
            quantization: 8.0
            units: REFLECTIVITY_SCALED
            log_scale: false
            range: {{min: 0.01, max: 0.5}}
        format:
            sensor_output_list:
            - output_name: "point_cloud"
              point_cloud_data:
                data_fields:
                - POSITION_X
                - POSITION_Y
                - POSITION_Z
                - INTENSITY
                handedness: RIGHT_HAND
# --------------------LOCALIZATION SENSOR------------------------------------------------                
    localization_sensors:
    - name: localization_0
      mount:
        px:  0
        py: 0
        pz:  0
        rpy:
          roll:   0.0
          pitch: 0.0
          yaw:    0.0
      sensor_output:
        reporting_frame: MAP  # Can also be set to VEHICLE or SENSOR.
triggered_messages:
  - message: "Collision"
    once:
        collision: {{ trigger_distance: 0.0 }}
v2_api_basic:
  interfaces:
  - name: default
  sources:
  - stack:
      name: default
  channels:
  - source: {{type: SIMIAN}}
    sink: {{type: VEHICLE_STACK}}
    name: "simian_time"
    type: TIME
    timing: {{hertz: {FREQUENCY}}}
  - source: {{type: SIMIAN}}
    sink: {{type: VEHICLE_STACK}}
    name: "simian_pose"
    type: POSE
    timing: {{hertz: {FREQUENCY}}}
  - source: {{type: SIMIAN}}
    sink: {{type: VEHICLE_STACK}}
    name: "simian_ground_truth_actors"
    type: ACTORS
    timing: {{hertz: {FREQUENCY}}}
  - source: {{type: VEHICLE_STACK}}
    sink: {{type: SIMIAN}}
    name: "simian_controls"
    type: CONTROLS
    timing: {{hertz: {FREQUENCY}}}
  - source: {{type: VEHICLE_STACK}}
    sink: {{type: SIMIAN}}
    name: "simian_stack_state"
    type: STACK_STATE
    timing: {{hertz: {FREQUENCY}}}
  - source: {{type: SIMIAN}}
    sink: {{type: VEHICLE_STACK}}
    name: "simian_behavior_predicted_control"
    type: CONTROLS
    timing: {{hertz: {FREQUENCY}}}
  - source: {{type: SIMIAN}}
    sink: {{type: VEHICLE_STACK}}
    name: "simian_motion_feedback"
    type: MOTION_FEEDBACK
    timing: {{hertz: {FREQUENCY}}}
  - source: {{type: SIMIAN}}
    sink: {{type: VEHICLE_STACK}}
    name: "simian_triggers"
    type: TRIGGER
    timing: {{hertz: {FREQUENCY}}}
  - source: {{type: SIMIAN}}
    sink: {{type: VEHICLE_STACK}}
    name: "simian_trip_agent"
    type: TRIP_AGENT
    timing: {{hertz: {FREQUENCY}}}
  - source: {{type: SIMIAN}}
    sink: {{type: VEHICLE_STACK}}
    name: "simian_perceived_actors"
    type: ACTORS
    timing: {{hertz: {FREQUENCY}}}
  - source: {{type: SIMIAN}}
    sink: {{type: VEHICLE_STACK}}
    name: "camera_0"
    type: CAMERA
    timing: {{hertz: {FREQUENCY}}}
  - source: {{type: SIMIAN}}
    sink: {{type: VEHICLE_STACK}}
    name: "lidar_0"
    type: PERCEPTION_SENSOR
    timing: {{hertz: {FREQUENCY}}}
  - source: {{type: SIMIAN}}
    sink: {{type: VEHICLE_STACK}}
    name: "localization_0"
    type: LOCALIZATION_SENSOR
    timing: {{hertz: {FREQUENCY}}}
"""

def random_sample_scenario_config(constraints):
    scenario_config = []
    for k in constraints.keys():
      if constraints[k][0]=="range":
          sampled_value = str(round(random.uniform(*constraints[k][1]),4))
          scenario_config.append(sampled_value)
      elif constraints[k][0]=="choice":
          sampled_value = str(random.choice(constraints[k][1]))
          scenario_config.append(sampled_value)
      else:
          raise NotImplementedError
    return scenario_config

def random_sample_fidelity_settings(constraints):
    fidelity_settings = {}
    for k in constraints.keys():
      if constraints[k][0]=="range":
          sampled_value = constraints[k][2](round(random.uniform(*constraints[k][1]),4))  #pass through the transformation function in case log transforms are applied
          fidelity_settings[k] = sampled_value
      elif constraints[k][0]=="choice":
          sampled_value = constraints[k][2](random.choice(constraints[k][1]))         #pass through the transformation function to be consistent with range constraint type
          fidelity_settings[k] = sampled_value
      else:
          raise NotImplementedError
    return fidelity_settings

def get_yaml_data(file):
    with open(file, 'r') as f:
        YAML = yaml.safe_load(f)
    return YAML


def write_to_yaml(file, updated_YAML):
    with open(file, 'w') as f:
        yaml.dump(updated_YAML, f)
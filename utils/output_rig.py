import json
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation as R


def get_extrinsic_matrices(calib_path: str, cam_name: str) -> np.ndarray:
    output_rig_map = {
        'reversed': [
            '210412',
            '210422',
            '0422',
            '210522',
            '210607',
            '210615',
            '210118',
        ],
        'not_reversed': [
            '210518',
            '210610',
            '210324',
            '210420',
            '210420',
            '210122',
            '210312',
        ]
    }

    calib_path = Path(calib_path)
    date = calib_path.stem[max(calib_path.stem.rfind('_'), calib_path.stem.rfind('-')) + 1:]
    date = ''.join([c for c in date if c.isdigit()])

    with calib_path.open(mode='r', encoding='utf-8') as f:
        data = json.load(f)

    sensors_cfg = data['rig']['sensors'][-1]
    sensor_map = {
        'cameraMainFov60': 'nominalSensor2cameraMainFov60',
        'cameraFov30': 'nominalSensor2cameraFov30',
        'cameraFov150': 'nominalSensor2cameraFov150',
    }

    sensor = sensor_map[cam_name]
    sensor_cfg = sensors_cfg[sensor]
    sensor_lidar = {
        'rpy': sensor_cfg['roll-pitch-yaw'],
        't': sensor_cfg['t']
    }

    if date in output_rig_map['not_reversed']:
        rotation_matrix = R.from_euler('ZYX', sensor_lidar['rpy'])
    elif date in output_rig_map['reversed']:
        rotation_matrix = R.from_euler('ZYX', sensor_lidar['rpy'][::-1])
    else:
        raise RuntimeError(f'Unsupported output-rig file {calib_path}')

    translation_vector = np.array(sensor_lidar['t'])

    extrinsic = np.zeros((3, 4), dtype=np.float32)
    extrinsic[:, 0:3] = rotation_matrix.as_matrix()
    extrinsic[:, 3] = np.array(translation_vector)

    return extrinsic


def get_intrinsic_matrices(calib_path: str, cam_name: str) -> np.ndarray:
    with open(calib_path, mode='r', encoding='utf-8') as f:
        data = json.load(f)

    sensors_cfg = data['rig']['sensors']

    for i in range(3):
        sensor_cfg = sensors_cfg[i]
        name = sensor_cfg.get('name', None)
        if name == cam_name:
            intrinsic_cfg = sensor_cfg.get('properties', None)

            cx = float(intrinsic_cfg['cx'])
            cy = float(intrinsic_cfg['cy'])
            fx = float(intrinsic_cfg['fx'])
            fy = float(intrinsic_cfg['fy'])

            intrinsic = np.array([
                [fx, 0, cx],
                [0, fy, cy],
                [0, 0, 1],
            ])
            break

    return intrinsic

from typing import Tuple

import numpy as np

from dto.bat3d.instance import Instance as BAT3DInstance
from dto.kitti.label.instance import Instance as KITTIInstance
from dto.pred.box3d import LiDARBox3D
from dto.scale_ai.instance import Instance as ScaleAIInstance
from dto.scale_ai.instance import Instance3D as ScaleAIInstance3D
from utils.kitti import calc_alpha, compute_box_3d
from utils.matrix import homo_mat, map_dimension, point_3d_transfrom


def bat3d_to_kitti(bat3d_instance: BAT3DInstance, extrinsic: np.ndarray, intrinsic: np.ndarray,
                   image_size: Tuple[int, int]) -> KITTIInstance:
    type_ = bat3d_instance.class_.replace(' ', '_') if bat3d_instance.class_ != 'Others' else 'DontCare'
    truncated = 0.0
    occluded = 0
    width = bat3d_instance.width
    height = bat3d_instance.height
    length = bat3d_instance.length
    x = bat3d_instance.x
    y = bat3d_instance.y
    z = bat3d_instance.z
    rotation_y = bat3d_instance.rotationY
    score = bat3d_instance.score
    track_id = bat3d_instance.trackId

    # Dimensions
    bat3d_dim_map = {
        'x': width,
        'y': length,
        'z': height,
    }
    cam_dim_map = {
        'width': 'x',
        'height': 'y',
        'length': 'z',
    }
    width, height, length = map_dimension(extrinsic, bat3d_dim_map, cam_dim_map)
    dimensions = (height, width, length)

    # Location
    location = np.array([[x, y, z]])
    location = point_3d_transfrom(location, extrinsic)[0]
    x, y, z = location
    y += height / 2
    location = (x, y, z)

    # Rotation Y
    rotation_y = - rotation_y - np.pi / 2
    rotation_y = np.arctan2(np.sin(rotation_y), np.cos(rotation_y))

    # BBox
    projection_mat = homo_mat(intrinsic)
    projection_mat = projection_mat[:3]
    bbox_8points, _ = compute_box_3d(width, height, length, location, rotation_y, projection_mat)

    if bbox_8points is not None:
        x_min = max(0, round(min(bbox_8points[:, 0])))
        x_max = min(round(max(bbox_8points[:, 0])), image_size[0])
        y_min = max(0, round(min(bbox_8points[:, 1])))
        y_max = min(round(max(bbox_8points[:, 1])), image_size[1])
    else:
        x_min = x_max = y_min = y_max = -10

    bbox = (x_min, y_min, x_max, y_max)

    # Alpha
    alpha = calc_alpha(location, rotation_y)
    return KITTIInstance(type_, truncated, occluded, bbox, alpha, dimensions, location, rotation_y, score, track_id)


def lidar_box3d_to_bat3d(lidar_box3d: LiDARBox3D, trackId: int, frameIdx: int, prelabel: bool = None) -> BAT3DInstance:
    class_ = lidar_box3d.type.replace('_', ' ') if lidar_box3d.type != 'DontCare' else 'Others'
    return BAT3DInstance(class_, lidar_box3d.x_size, lidar_box3d.y_size, lidar_box3d.z_size, lidar_box3d.x,
                         lidar_box3d.y, lidar_box3d.z, lidar_box3d.rotation_y, trackId, frameIdx, lidar_box3d.score,
                         prelabel)


def lidar_box3d_to_kitti(lidar_box3d: LiDARBox3D, Tr_velo_to_cam: np.ndarray, cam_to_image: np.ndarray,
                         image_size: Tuple[int, int]) -> KITTIInstance:
    bat3d_instance = lidar_box3d_to_bat3d(lidar_box3d, 0, 0)
    kitti_instance = bat3d_to_kitti(bat3d_instance, Tr_velo_to_cam, cam_to_image, image_size)
    return kitti_instance


def scale_ai_to_bat3d(scale_ai_instance: ScaleAIInstance, track_id: int, frame_id: int) -> BAT3DInstance:
    if isinstance(scale_ai_instance, ScaleAIInstance3D):
        class_ = scale_ai_instance.label
        width = scale_ai_instance.dimensions.x
        length = scale_ai_instance.dimensions.y
        height = scale_ai_instance.dimensions.z
        x = scale_ai_instance.position.x
        y = scale_ai_instance.position.y
        z = scale_ai_instance.position.z
        rotationY = scale_ai_instance.yaw
        bat3d_instance = BAT3DInstance(class_, width, length, height, x, y, z, rotationY, track_id, frame_id)
    else:
        raise NotImplementedError

    return bat3d_instance

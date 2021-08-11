from typing import List, Tuple

import numpy as np
from mmdet3d.apis import inference_detector, init_model
from mmdet3d.core.bbox import LiDARInstance3DBoxes

from abstract.processor import Processor
from dto.kitti.velodyne.velodyne import Velodyne
from dto.pred.box3d import LiDARBox3D
from dto.seq.seq_info import SeqInfo
from utils.common import abs_path
from utils.matrix import inv_mat, map_dimension, point_3d_transfrom


class Detector(Processor):
    def __init__(self, config_path: str, checkpoint_path: str, classes: List[str], device: str = 'cuda:0'):
        super(Detector, self).__init__()
        self.config_path = abs_path(config_path)
        self.checkpoint_path = abs_path(checkpoint_path)
        self.classes = classes
        self.device = device
        self.model = init_model(self.config_path, self.checkpoint_path, device=device)

    def process(self, seq_info: SeqInfo, velodyne_dir: str) -> Tuple[SeqInfo, List[List[LiDARBox3D]]]:
        velodyne = Velodyne.parse(velodyne_dir)
        frames = []
        assert seq_info.bin_pc_transform_matrix is not None

        for frame in velodyne.frames:
            result, _ = inference_detector(self.model, frame.frame_file)
            result = result[0]
            frames.append(self.get_result_info(result, seq_info.bin_pc_transform_matrix))

        return seq_info, frames

    def get_result_info(self, result: LiDARInstance3DBoxes, bin_pc_transform_matrix: np.ndarray) -> List[LiDARBox3D]:
        boxes_3d = result['boxes_3d'].tensor
        scores_3d = result['scores_3d']
        labels_3d = result['labels_3d']
        instances = []

        for bbox_3d, score_3d, label_3d in zip(boxes_3d, scores_3d, labels_3d):
            x, y, z, x_size, y_size, z_size, yaw = bbox_3d
            x, y, z, x_size, y_size, z_size, yaw, score_3d = map(float, [x, y, z, x_size, y_size, z_size,
                                                                         yaw, score_3d])
            label_3d = self.classes[label_3d]

            # Rotation Y
            rotation_y = - (yaw - np.pi) - np.pi / 2
            rotation_y = np.arctan2(np.sin(rotation_y), np.cos(rotation_y))

            # Location
            z += z_size / 2
            inv_bin_pc_transform_matrix = inv_mat(bin_pc_transform_matrix)
            location = np.array([[x, y, z]])
            location = point_3d_transfrom(location, inv_bin_pc_transform_matrix)[0]
            x, y, z = location

            # Dimesions
            lidar_box3d_dim_map = {
                'x': y_size,
                'y': x_size,
                'z': z_size,
            }
            lidar_dim_map = {
                'width': 'x',
                'length': 'y',
                'height': 'z',
            }
            x_size, z_size, y_size = map_dimension(inv_bin_pc_transform_matrix, lidar_box3d_dim_map, lidar_dim_map)

            instance = LiDARBox3D(label_3d, x, y, z, x_size, y_size, z_size, rotation_y, score_3d)
            instances.append(instance)

        return instances

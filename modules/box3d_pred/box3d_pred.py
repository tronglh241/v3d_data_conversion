from pathlib import Path
from typing import Any, List, Tuple

import numpy as np

from abstract.stage import Stage
from dto.pred.box3d import LiDARBox3D
from dto.seq.seq_info import SeqInfo
from utils.matrix import homo_mat, point_3d_transfrom


class Box3DPred(Stage):
    def __init__(self, data_dir: str = 'velodyne', ret_labels: List[str] = None, thres_score: float = 0.5,
                 **kwargs: Any):
        super(Box3DPred, self).__init__(**kwargs)
        self.data_dir = data_dir
        self.ret_labels = ret_labels
        self.thres_score = thres_score

    def preprocess(self, seq_info: SeqInfo) -> Tuple[SeqInfo, str]:
        data_dir = str(Path(seq_info.out_dir).joinpath(seq_info.seq_name, self.data_dir))
        return seq_info, data_dir

    def postprocess(self, seq_info: SeqInfo, frames: List[List[LiDARBox3D]]) -> Tuple[SeqInfo, List[List[LiDARBox3D]]]:
        extrinsic = seq_info.extrinsic
        intrinsic = seq_info.intrinsic
        image_size = seq_info.image_size
        assert extrinsic is not None
        assert intrinsic is not None
        assert image_size is not None

        for i, frame in enumerate(frames):
            for lidar_box3d in frame:
                if (self.ret_labels is not None and lidar_box3d.type not in self.ret_labels
                    or (lidar_box3d.score is not None and lidar_box3d.score < self.thres_score)
                        or not self.is_in_fov(lidar_box3d, image_size, extrinsic, intrinsic)):
                    lidar_box3d.type = 'ignore'
            frame = list(filter(lambda lidar_box3d: lidar_box3d.type != 'ignore', frame))
            frames[i] = frame
        return seq_info, frames

    def is_in_fov(self, lidar_box3d: LiDARBox3D, image_size: Tuple[int, int],
                  extrinsic: np.ndarray, intrinsic: np.ndarray) -> bool:
        location = (lidar_box3d.x, lidar_box3d.y, lidar_box3d.z)
        location = self.point_to_image(location, extrinsic, intrinsic)

        return 0 < location[0] < image_size[0] and 0 < location[1] < image_size[1]

    def point_to_image(self, location: Tuple[float, float, float], extrinsic: np.ndarray,
                       intrinsic: np.ndarray) -> Tuple[int, int]:
        points = np.array([location])
        extrinsic = homo_mat(extrinsic)
        intrinsic = homo_mat(intrinsic)
        projection_mat = intrinsic @ extrinsic
        projection_mat = projection_mat[:3]
        points = point_3d_transfrom(points, projection_mat)
        points /= points[:, 2:]
        return (points[0][0], points[0][1])

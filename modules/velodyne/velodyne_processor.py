from pathlib import Path
from typing import Iterator, List, Tuple

import numpy as np

from abstract.processor import Processor
from dto.kitti.velodyne.frame import Frame
from dto.seq.seq_info import SeqInfo
from utils.matrix import point_3d_transfrom


class VelodyneProcessor(Processor):
    def __init__(self, velodyne_dir: str = 'velodyne', n_feature: int = 4) -> None:
        self.velodyne_dir = velodyne_dir
        self.n_feature = n_feature  # number of features of a point, e.g (x, y, z, intensity)

    def process(self, seq_info: SeqInfo, frame_names: List[str], point_clouds: Iterator[np.ndarray]) -> Tuple[SeqInfo]:
        out_dir = str(Path(seq_info.out_dir).joinpath(seq_info.seq_name, self.velodyne_dir))

        assert isinstance(seq_info.bin_pc_transform_matrix, np.ndarray)
        assert seq_info.bin_pc_transform_matrix.shape == (3, 4)
        bin_pc_transform_matrix = seq_info.bin_pc_transform_matrix

        for frame_name, point_cloud in zip(frame_names, point_clouds):
            point_cloud = self.process_pcd(point_cloud, bin_pc_transform_matrix)
            assert point_cloud.dtype == np.float32, point_cloud.dtype
            frame = Frame(int(frame_name), data=point_cloud)
            frame.tofile(out_dir)

        return seq_info,

    def process_pcd(self, point_cloud: np.ndarray, bin_pc_transform_matrix: np.ndarray) -> np.ndarray:
        point_cloud = point_cloud[:, :self.n_feature].astype(np.float32)
        point_cloud[:, :3] = point_3d_transfrom(point_cloud[:, :3], bin_pc_transform_matrix)
        return point_cloud

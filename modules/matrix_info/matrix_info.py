from typing import Tuple

import numpy as np
from scipy.spatial.transform import Rotation as R

from abstract.stage import Stage
from dto.seq.seq_info import SeqInfo
from utils.matrix import homo_mat, inv_mat


class MatrixInfo(Stage):
    def preprocess(self, seq_info: SeqInfo, calib_file: str, extrinsic: np.ndarray,
                   intrinsic: np.ndarray) -> Tuple[SeqInfo]:
        seq_info.extrinsic = extrinsic
        seq_info.intrinsic = intrinsic
        seq_info.calib_file = calib_file

        # # Original
        # seq_info.bin_pc_transform_matrix = np.identity(4)[:3]
        # seq_info.calib_extrinsic = extrinsic

        # Convert to kitti coordinate system
        kitti_velo_to_cam = self.kitti_velo_to_cam_matrix(extrinsic)
        seq_info.calib_extrinsic = kitti_velo_to_cam

        bin_pc_transform_matrix = inv_mat(kitti_velo_to_cam, ret_homo=True) @ homo_mat(extrinsic)
        bin_pc_transform_matrix = bin_pc_transform_matrix[:3]

        seq_info.bin_pc_transform_matrix = bin_pc_transform_matrix
        return seq_info,

    def kitti_velo_to_cam_rotation_matrix(self) -> np.ndarray:
        Rn = R.from_euler('ZYX', [np.pi / 2, -np.pi / 2, 0]).as_matrix()
        Rn = np.pad(Rn, ((0, 0), (0, 1)))
        assert Rn.shape == (3, 4)
        return Rn

    def kitti_velo_to_cam_matrix(self, extrinsic: np.ndarray) -> np.ndarray:
        assert extrinsic.shape == (3, 4)
        translation_vector = extrinsic[:, 3]
        kitti_velo_to_cam = self.kitti_velo_to_cam_rotation_matrix()
        kitti_velo_to_cam[:, 3] = translation_vector
        assert kitti_velo_to_cam.shape == (3, 4)
        return kitti_velo_to_cam

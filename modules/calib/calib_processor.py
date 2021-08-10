from pathlib import Path
from typing import Tuple

import numpy as np

from abstract.processor import Processor
from dto.kitti.calib.calib import Calib
from dto.kitti.calib.frame import Frame
from dto.seq.seq_info import SeqInfo


class CalibProcessor(Processor):
    def __init__(self, calib_dir: str = 'calib', image_size: Tuple[int, int] = None, padding: bool = True) -> None:
        self.calib_dir = calib_dir
        self.image_size = image_size
        self.padding = padding

    def process(self, seq_info: SeqInfo) -> Tuple[SeqInfo]:
        out_dir = str(Path(seq_info.out_dir).joinpath(seq_info.seq_name, self.calib_dir))
        org_image_size = seq_info.image_size
        extrinsic = seq_info.calib_extrinsic
        intrinsic = seq_info.calib_intrinsic
        frame_names = seq_info.frame_names
        assert org_image_size is not None
        assert extrinsic is not None
        assert intrinsic is not None
        assert frame_names is not None

        assert extrinsic.shape == (3, 4), extrinsic.shape
        assert intrinsic.shape == (3, 3), intrinsic.shape
        P0 = P1 = P3 = Tr_imu_to_velo = np.identity(4)[:3]
        P2 = intrinsic

        if self.image_size is not None:
            P2 = self.pad_resize(P2, org_image_size)

        seq_info.calib_intrinsic = P2
        P2 = np.pad(P2, ((0, 0), (0, 1)))
        R0_rect = np.identity(3)
        Tr_velo_to_cam = extrinsic

        frames = [Frame(int(frame_name), P0, P1, P2, P3, R0_rect, Tr_velo_to_cam, Tr_imu_to_velo)
                  for frame_name in frame_names]
        calib = Calib(frames)
        calib.tofile(out_dir)

        return seq_info,

    def pad_resize(self, intrinsic: np.ndarray, org_image_size: Tuple[int, int]) -> np.ndarray:
        assert self.image_size is not None
        width, height = org_image_size

        if self.padding:
            scale_x = scale_y = min(self.image_size[0] / width, self.image_size[1] / height)
        else:
            scale_x = self.image_size[0] / width
            scale_y = self.image_size[1] / height

        scale_mat = np.array([
            [scale_x, 0, 0],
            [0, scale_y, 0],
            [0, 0, 1],
        ])
        intrinsic = scale_mat @ intrinsic

        return intrinsic

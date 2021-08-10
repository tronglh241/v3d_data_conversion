from __future__ import annotations

from pathlib import Path

import numpy as np

from abstract.dto import DTO
from utils.common import open_file


class Frame(DTO):
    def __init__(self, frame_id: int, P0: np.ndarray, P1: np.ndarray, P2: np.ndarray, P3: np.ndarray,
                 R0_rect: np.ndarray, Tr_velo_to_cam: np.ndarray, Tr_imu_to_velo: np.ndarray):
        super(Frame, self).__init__()
        self.frame_id = frame_id
        self.P0 = P0
        self.P1 = P1
        self.P2 = P2
        self.P3 = P3
        self.R0_rect = R0_rect
        self.Tr_velo_to_cam = Tr_velo_to_cam
        self.Tr_imu_to_velo = Tr_imu_to_velo

    @property
    def name(self) -> str:
        return f'{self.frame_id:06d}.txt'

    @classmethod
    def parse(cls, frame_file: str) -> Frame:
        mat_shape = {
            'P0': (3, 4),
            'P1': (3, 4),
            'P2': (3, 4),
            'P3': (3, 4),
            'R0_rect': (3, 3),
            'Tr_velo_to_cam': (3, 4),
            'Tr_imu_to_velo': (3, 4),
        }

        frame_id = int(Path(frame_file).stem)
        mats = {}
        with open(frame_file, mode='r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(':')
                    mat_name = parts[0].strip()
                    mat_value = [float(ele) for ele in parts[1].strip().split()]
                    mat_value = np.array(mat_value).reshape(mat_shape[mat_name])
                    mats[mat_name] = mat_value

        return cls(frame_id, **mats)

    def tofile(self, calib_dir: str) -> None:
        mats = {
            'P0': self.P0,
            'P1': self.P1,
            'P2': self.P2,
            'P3': self.P3,
            'R0_rect': self.R0_rect,
            'Tr_velo_to_cam': self.Tr_velo_to_cam,
            'Tr_imu_to_velo': self.Tr_imu_to_velo,
        }

        lines = [f'{key}: ' + ' '.join([str(ele.item()) for ele in value.ravel()]) + '\n'
                 for key, value in mats.items()]

        frame_file = str(Path(calib_dir).joinpath(self.name))
        with open_file(frame_file, mode='w', encoding='utf-8') as f:
            f.writelines(lines)

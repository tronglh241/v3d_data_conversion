from pathlib import Path
from typing import Any, List, Optional, Tuple

import numpy as np

from abstract.dto import DTO

from .frame_info import FrameInfo


class SeqInfo(DTO):
    def __init__(self, seq_dir: str, out_dir: str):
        super(SeqInfo, self).__init__()
        self.seq_dir = seq_dir
        self.out_dir = out_dir

        self.extrinsic: Optional[np.ndarray] = None
        self.intrinsic: Optional[np.ndarray] = None
        self.calib_extrinsic: Optional[np.ndarray] = None
        self.calib_intrinsic: Optional[np.ndarray] = None
        self.bin_pc_transform_matrix: Optional[np.ndarray] = None

        self.pcd_file: Optional[str] = None
        self.image_file: Optional[str] = None
        self.calib_file: Optional[str] = None
        self.frame_names: Optional[List[str]] = None
        self.frame_infos: Optional[List[FrameInfo]] = None

        self.image_size: Optional[Tuple[int, int]] = None
        self.resized_image_size: Optional[Tuple[int, int]] = None

    @property
    def seq_name(self) -> str:
        seq_dir = Path(self.seq_dir)
        return seq_dir.name

    def get_frame_info(self, frame_name: str) -> Optional[FrameInfo]:
        frame_info = None

        if self.frame_infos:
            for info in self.frame_infos:
                if info.frame_name == frame_name:
                    frame_info = info
                    break

        return frame_info

    def set_frame_info(self, frame_name: str, **kwargs: Any) -> None:
        frame_info = self.get_frame_info(frame_name)

        if frame_info is not None:
            for key, value in kwargs.items():
                if hasattr(frame_info, key):
                    setattr(frame_info, key, value)
                else:
                    super(SeqInfo, self).__setattr__(key, value)
        else:
            frame_info = FrameInfo(frame_name, **kwargs)

            if self.frame_infos is None:
                self.frame_infos = []

            self.frame_infos.append(frame_info)

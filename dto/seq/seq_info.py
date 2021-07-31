from pathlib import Path
from typing import Optional

import numpy as np

from abstract.dto import DTO


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

        self.calib_file: Optional[str] = None

    @property
    def seq_name(self) -> str:
        seq_dir = Path(self.seq_dir)
        return seq_dir.name

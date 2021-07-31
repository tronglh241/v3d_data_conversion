from typing import Tuple

import numpy as np

from abstract.adapter import InAdapter
from dto.seq.seq_info import SeqInfo
from utils.common import get_file_with_stem
from utils.output_rig import get_extrinsic_matrices, get_intrinsic_matrices


class BAT3DInAdapter(InAdapter):
    def __init__(self, out_rig_stem: str = 'output-rig-*', cam_name: str = 'cameraMainFov60'):
        super(BAT3DInAdapter, self).__init__()
        self.out_rig_stem = out_rig_stem
        self.cam_name = cam_name

    def convert(self, stage_input: Tuple) -> Tuple[SeqInfo, str, np.ndarray, np.ndarray]:
        seq_info = stage_input[0]
        calib_file = get_file_with_stem(seq_info.seq_dir, self.out_rig_stem)

        if calib_file is None:
            raise FileNotFoundError(f'Ouput rig file not found in {seq_info.seq_dir}.')

        extrinsic = get_extrinsic_matrices(str(calib_file), self.cam_name)
        intrinsic = get_intrinsic_matrices(str(calib_file), self.cam_name)

        return seq_info, calib_file, extrinsic, intrinsic

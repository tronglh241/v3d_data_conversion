from typing import Tuple

from abstract.stage import Stage
from dto.seq.seq_info import SeqInfo


class Calib(Stage):
    def preprocess(self, seq_info: SeqInfo) -> Tuple[SeqInfo]:
        frame_names = seq_info.frame_names
        calib_file = seq_info.calib_file
        assert frame_names is not None
        assert calib_file is not None

        for frame_name in frame_names:
            seq_info.set_frame_info(frame_name, calib_file=calib_file)

        return seq_info,

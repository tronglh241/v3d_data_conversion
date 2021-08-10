from typing import Iterator, List, Tuple

import numpy as np

from abstract.stage import Stage
from dto.seq.seq_info import SeqInfo


class Velodyne(Stage):
    def preprocess(self, seq_info: SeqInfo, frame_names: List[str], pcd_files: List[str],
                   point_clouds: Iterator[np.ndarray]) -> Tuple[SeqInfo, List[str], Iterator[np.ndarray]]:
        for frame_name, pcd_file in zip(frame_names, pcd_files):
            seq_info.set_frame_info(frame_name, pcd_file=pcd_file)

        return seq_info, frame_names, point_clouds

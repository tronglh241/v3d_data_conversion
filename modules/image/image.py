from typing import Iterator, List, Tuple

import numpy as np

from abstract.stage import Stage
from dto.seq.seq_info import SeqInfo


class Image(Stage):
    def preprocess(self, seq_info: SeqInfo, frame_names: List[str], image_files: List[str],
                   images: Iterator[np.ndarray]) -> Tuple[SeqInfo, List[str], Iterator[np.ndarray]]:
        for frame_name, image_file in zip(frame_names, image_files):
            seq_info.set_frame_info(frame_name, image_file=image_file)

        return seq_info, frame_names, images

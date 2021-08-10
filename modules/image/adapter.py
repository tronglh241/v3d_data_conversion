from pathlib import Path
from typing import Iterator, List, Tuple, Union

import cv2
import numpy as np
from natsort import natsorted

from abstract.adapter import InAdapter
from dto.seq.seq_info import SeqInfo
from utils.common import get_file_with_stem


class BAT3DInAdapter(InAdapter):
    def __init__(self, image_dir: str = 'images/CAM_FRONT_LEFT', image_suffix: str = '.jpeg',
                 file_id: Union[int, list, tuple] = None):
        super(BAT3DInAdapter, self).__init__()
        self.image_dir = image_dir
        self.image_suffix = image_suffix

        if isinstance(file_id, int):
            file_id = [file_id]
        elif isinstance(file_id, tuple):
            file_id = list(range(*file_id))

        self.file_id = file_id

    def convert(self, stage_input: Tuple[SeqInfo]) -> Tuple[SeqInfo, List[str], List[str], Iterator[np.float32]]:
        seq_info = stage_input[0]
        image_dir = Path(seq_info.seq_dir).joinpath(self.image_dir)
        frame_names = seq_info.frame_names

        if frame_names is None:
            image_files = natsorted(image_dir.glob(f'*{self.image_suffix}'), key=lambda file: file.stem)

            if self.file_id is not None:
                image_files = [image_files[i] for i in self.file_id]

            frame_names = [image_file.stem for image_file in image_files]
            image_files = [str(image_file.resolve()) for image_file in image_files]
        else:
            files = [get_file_with_stem(str(image_dir), frame_name) for frame_name in frame_names]

            for i, file in enumerate(files):
                if file is None:
                    frame_names[i] = ''

            image_files = [file for file in files if file]
            frame_names = [frame_name for frame_name in frame_names if frame_name]

        seq_info.frame_names = frame_names
        images = (cv2.imread(image_file) for image_file in image_files)
        return seq_info, frame_names, image_files, images

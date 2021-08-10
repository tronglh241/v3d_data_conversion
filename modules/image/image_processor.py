from pathlib import Path
from typing import Iterator, List, Tuple

import cv2
import numpy as np

from abstract.processor import Processor
from dto.kitti.image.frame import Frame
from dto.seq.seq_info import SeqInfo


class ImageProcessor(Processor):
    def __init__(self, image_dir: str = 'image_2', image_size: Tuple[int, int] = None, padding: bool = True) -> None:
        self.image_dir = image_dir
        self.image_size = image_size
        self.padding = padding

    def process(self, seq_info: SeqInfo, frame_names: List[str], images: Iterator[np.ndarray]) -> Tuple[SeqInfo]:
        out_dir = str(Path(seq_info.out_dir).joinpath(seq_info.seq_name, self.image_dir))

        for frame_name, image in zip(frame_names, images):
            if seq_info.image_size is None:
                seq_info.image_size = (image.shape[1], image.shape[0])
            elif seq_info.image_size != image.shape[1::-1]:
                raise RuntimeError(f'Sizes of images in {seq_info.seq_dir} are not the same.')

            if self.image_size is not None:
                image = self.pad_resize(image)

            seq_info.resized_image_size = (image.shape[1], image.shape[0])
            frame = Frame(int(frame_name), data=image)
            frame.tofile(out_dir)

        return seq_info,

    def pad_resize(self, image: np.ndarray) -> np.ndarray:
        assert self.image_size is not None

        # resize
        width, height = image.shape[1::-1]

        if self.padding:
            scale_x = scale_y = min(self.image_size[0] / width, self.image_size[1] / height)
        else:
            scale_x = self.image_size[0] / width
            scale_y = self.image_size[1] / height

        image = cv2.resize(image, (0, 0), fx=scale_x, fy=scale_y)

        # pad
        width, height = image.shape[1::-1]
        padding = (self.image_size[1] - height, self.image_size[0] - width)
        image = np.pad(image, ((0, padding[0]), (0, padding[1]), (0, 0)))

        return image

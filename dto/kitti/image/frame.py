from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from abstract.dto import DTO


class Frame(DTO):
    def __init__(self, frame_id: int, frame_file: str = None, data: np.ndarray = None):
        super(Frame, self).__init__()
        if frame_file is None and data is None:
            raise ValueError('`frame_file` or `data` must be provided.')

        self.frame_id = frame_id
        self.frame_file = frame_file
        self._data = data

    @property
    def data(self) -> np.ndarray:
        if self._data is None:
            return cv2.imread(self.frame_file)
        else:
            return self._data

    @property
    def name(self) -> str:
        return f'{self.frame_id:06d}.png'

    @classmethod
    def parse(cls, frame_file: str) -> Frame:
        frame_id = int(Path(frame_file).stem)
        return cls(frame_id, frame_file)

    def tofile(self, image_dir: str) -> None:
        image_file = Path(image_dir).joinpath(self.name)
        image_file.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(image_file), self.data)

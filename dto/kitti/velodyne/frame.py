from __future__ import annotations

from pathlib import Path

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
            return np.fromfile(self.frame_file, dtype=np.float32)
        else:
            return self._data

    @data.setter
    def data(self, dt: np.ndarray) -> None:
        self._data = dt.astype(np.float32)

    @property
    def name(self) -> str:
        return f'{self.frame_id:06d}.bin'

    @classmethod
    def parse(cls, frame_file: str) -> Frame:
        frame_id = int(Path(frame_file).stem)
        return cls(frame_id, frame_file)

    def tofile(self, velodyne_dir: str) -> None:
        bin_file = Path(velodyne_dir).joinpath(self.name)
        bin_file.parent.mkdir(parents=True, exist_ok=True)
        self.data.tofile(str(bin_file))

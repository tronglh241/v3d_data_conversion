from __future__ import annotations

from pathlib import Path
from typing import List

from natsort import natsorted

from abstract.dto import DTO

from .frame import Frame


class Velodyne(DTO):
    def __init__(self, frames: List[Frame]):
        super(Velodyne, self).__init__()
        self.frames = frames

    @classmethod
    def parse(cls, velodyne_dir: str) -> Velodyne:
        frame_files = natsorted(Path(velodyne_dir).glob('*.bin'), key=lambda file: file.stem)
        frames = [Frame.parse(str(frame_file)) for frame_file in frame_files]
        return cls(frames)

    def tofile(self, velodyne_dir: str) -> None:
        for frame in self.frames:
            frame.tofile(velodyne_dir)

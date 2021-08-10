from __future__ import annotations

from pathlib import Path
from typing import List

from natsort import natsorted

from abstract.dto import DTO

from .frame import Frame


class Calib(DTO):
    def __init__(self, frames: List[Frame]):
        super(Calib, self).__init__()
        self.frames = frames

    @classmethod
    def parse(cls, calib_dir: str) -> Calib:
        frame_files = natsorted(Path(calib_dir).glob('*.txt'), key=lambda file: file.stem)
        frames = [Frame.parse(str(frame_file)) for frame_file in frame_files]
        return cls(frames)

    def tofile(self, calib_dir: str) -> None:
        for frame in self.frames:
            frame.tofile(calib_dir)

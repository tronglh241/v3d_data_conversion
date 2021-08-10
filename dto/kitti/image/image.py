from __future__ import annotations

from pathlib import Path
from typing import List

from natsort import natsorted

from abstract.dto import DTO

from .frame import Frame


class Image(DTO):
    def __init__(self, frames: List[Frame]):
        super(Image, self).__init__()
        self.frames = frames

    @classmethod
    def parse(cls, image_dir: str) -> Image:
        frame_files = natsorted(Path(image_dir).glob('*.png'), key=lambda file: file.stem)
        frames = [Frame.parse(str(frame_file)) for frame_file in frame_files]
        return cls(frames)

    def tofile(self, image_dir: str) -> None:
        for frame in self.frames:
            frame.tofile(image_dir)

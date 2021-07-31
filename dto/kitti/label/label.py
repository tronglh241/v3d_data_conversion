from __future__ import annotations

from pathlib import Path
from typing import List

from natsort import natsorted

from .base import Element
from .frame import Frame


class Label(Element):
    def __init__(self, frames: List[Frame]):
        super(Label, self).__init__()
        self.frames = frames

    @classmethod
    def parse(cls, label_dir: str) -> Label:
        frame_files = natsorted(Path(label_dir).glob('*.txt'))
        frames = [Frame.parse(str(frame_file)) for frame_file in frame_files]
        return cls(frames)

    def tofile(self, label_dir: str) -> None:
        for frame in self.frames:
            frame.tofile(label_dir)

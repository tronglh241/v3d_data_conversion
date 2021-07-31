from __future__ import annotations

import json
from typing import List

from utils.common import open_file

from .base import Element
from .frame import Frame


class Label(Element):
    def __init__(self, frames: List[Frame], file_path: str = None):
        super(Label, self).__init__()
        self.frames = frames
        self.file_path = file_path

    @classmethod
    def parse(cls, anno: List[List[dict]], file_path: str = None) -> Label:
        frames = [Frame.parse(frame, i) for i, frame in enumerate(anno)]
        return cls(frames, file_path)

    @property
    def json(self) -> List[List[dict]]:
        obj = [frame.json for frame in self.frames]
        return obj

    @classmethod
    def fromfile(cls, file_path: str) -> Label:
        with open_file(file_path, mode='r', encoding='utf-8') as f:
            anno = json.load(f)

        return cls.parse(anno, file_path)

    def tofile(self, file_path: str) -> None:
        with open_file(file_path, mode='w') as f:
            json.dump(self.json, f, indent=4)

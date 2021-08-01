from __future__ import annotations

import json as js
from typing import List, Type

from utils.common import open_file

from .base import Element
from .frame import Frame, Frame2D, Frame3D


class Label(Element):
    supported_frame_types: List[Type[Frame]] = [
        Frame2D,
        Frame3D,
    ]

    def __init__(self, frames: List[Frame]):
        super(Label, self).__init__()
        self.frames = frames

    @classmethod
    def parse(cls, label: list) -> Label:
        frames = []

        for i, frame in enumerate(label):
            for frame_type in Label.supported_frame_types:
                if frame_type.is_compatitable(frame):
                    frames.append(frame_type.parse(i, frame))

        return cls(frames)

    @property
    def json(self) -> list:
        label = [frame.json for frame in self.frames]
        return label

    @staticmethod
    def fromfile(label_file: str) -> Label:
        with open(label_file, mode='r', encoding='utf-8') as f:
            obj = js.load(f)

        if not isinstance(obj, list):
            raise RuntimeError('JSON object must be a list.')

        label = Label.parse(obj)
        return label

    def tofile(self, label_file: str) -> None:
        with open_file(label_file, mode='w', encoding='utf-8') as f:
            js.dump(self.json, f, ensure_ascii=False, indent=4)

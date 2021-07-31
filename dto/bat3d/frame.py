from __future__ import annotations

from typing import List

from .base import Element
from .instance import Instance


class Frame(Element):
    def __init__(self, frame_id: int, instances: List[Instance]):
        super(Frame, self).__init__()
        self.instances = instances
        self.frame_id = frame_id

    @classmethod
    def parse(cls, frame: List[dict], frame_id: int) -> Frame:
        instances = [Instance.parse(instance) for instance in frame]
        return cls(frame_id, instances)

    @property
    def json(self) -> List[dict]:
        obj = [instance.json for instance in self.instances]
        return obj

    @property
    def name(self) -> str:
        return f'{self.frame_id:06d}'

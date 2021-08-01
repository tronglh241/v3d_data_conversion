from __future__ import annotations

from typing import Any, Dict, List, Optional, Type

from .base import Element
from .instance import Instance, Instance2D, Instance3D


class Frame(Element):
    keyword: Optional[str] = None
    supported_instance_types: List[Type[Instance]] = [
        Instance2D,
        Instance3D,
    ]

    def __init__(self, frame_id: int, instances: List[Instance]):
        super(Frame, self).__init__()
        self.frame_id = frame_id
        self.instances = instances

    @classmethod
    def parse(cls, frame_id: int, frame: Dict[str, list]) -> Frame:
        instances: List[Instance] = []

        if cls.keyword is None:
            raise ValueError('Class `keyword` must be not None.')

        for instance in frame[cls.keyword]:
            for instance_type in Frame.supported_instance_types:
                if instance_type.is_compatitable(instance):
                    instances.append(instance_type.parse(instance))

        return cls(frame_id, instances)

    @property
    def json(self) -> dict:
        frame = {
            type(self).keyword: [instance.json for instance in self.instances]
        }
        return frame

    @classmethod
    def is_compatitable(cls, frame: Any) -> bool:
        return isinstance(frame, dict) and len(frame) == 1 and cls.keyword in frame


class Frame2D(Frame):
    keyword = 'camera_responses'


class Frame3D(Frame):
    keyword = 'cuboids'

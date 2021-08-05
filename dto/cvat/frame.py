from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import List

from .base import Element
from .instance import Instance


class Frame(Element):
    tag = 'image'

    def __init__(self, height: int, id_: int, name: str, width: int, instances: List[Instance]):
        super(Frame, self).__init__()
        self.height = height
        self.id = id_
        self.name = name
        self.width = width
        self.instances = instances

    @classmethod
    def parse(cls, frame: ET.Element) -> Frame:
        if frame.tag != cls.tag:
            raise RuntimeError(f'Incompatitable tag, {cls.tag} required, {frame.tag} found.')
        height = int(frame.attrib['height'])
        id_ = int(frame.attrib['id'])
        name = frame.attrib['name']
        width = int(frame.attrib['width'])
        instances = [Instance.parse(instance) for instance in frame]
        return cls(height, id_, name, width, instances)

    @property
    def xml(self) -> ET.Element:
        attrib = {
            'height': str(self.height),
            'id': str(self.id),
            'name': self.name,
            'width': str(self.width),
        }
        ele = ET.Element(self.tag, attrib)
        ele.extend([instance.xml for instance in self.instances])
        return ele

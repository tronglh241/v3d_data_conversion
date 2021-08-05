from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import List
from xml.dom import minidom

from utils.common import open_file

from .base import Element
from .frame import Frame


class Label(Element):
    tag = 'annotation'

    def __init__(self, frames: List[Frame]):
        super(Label, self).__init__()
        self.frames = frames

    @classmethod
    def parse(cls, anno: ET.Element) -> Label:
        if anno.tag != cls.tag:
            raise RuntimeError(f'Incompatitable tag, {cls.tag} required, {anno.tag} found.')
        frames = [Frame.parse(frame) for frame in anno]
        return cls(frames)

    @property
    def xml(self) -> ET.Element:
        ele = ET.Element(self.tag)
        ele.extend([frame.xml for frame in self.frames])
        return ele

    @staticmethod
    def fromfile(anno_file: str) -> Label:
        root = ET.parse(anno_file).getroot()
        return Label.parse(root)

    def tofile(self, anno_file: str) -> None:
        with open_file(anno_file, mode='w') as f:
            xmlstr = minidom.parseString(ET.tostring(self.xml)).childNodes[0].toprettyxml(indent='    ')
            f.write(xmlstr)

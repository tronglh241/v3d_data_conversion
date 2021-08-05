from __future__ import annotations

import xml.etree.ElementTree as ET

from .base import Element


class Attrib(Element):
    tag = 'attribute'

    def __init__(self, name: str, value: str = None):
        super(Attrib, self).__init__()
        self.name = name
        self.value = value

    @classmethod
    def parse(cls, attrib: ET.Element) -> Attrib:
        if attrib.tag != cls.tag:
            raise RuntimeError(f'Incompatitable tag, {cls.tag} required, {attrib.tag} found.')
        name = attrib.attrib['name']
        value = attrib.text
        return cls(name, value)

    @property
    def xml(self) -> ET.Element:
        attrib = {
            'name': self.name,
        }
        ele = ET.Element(self.tag, attrib)
        if self.value is not None:
            ele.text = self.value
        return ele

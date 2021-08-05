from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import List, Optional

from .attrib import Attrib
from .base import Element


class Instance(Element):
    tag = 'cuboid'

    def __init__(self, frame: int, keyframe: int, label: str, occluded: int, outside: int, source: str,
                 xbl1: float, xbl2: float, xbr1: float, xbr2: float, xtl1: float, xtl2: float, xtr1: float, xtr2: float,
                 ybl1: float, ybl2: float, ybr1: float, ybr2: float, ytl1: float, ytl2: float, ytr1: float, ytr2: float,
                 z_order: int, attribs: List[Attrib]):
        super(Instance, self).__init__()
        self.frame = frame
        self.keyframe = keyframe
        self.label = label
        self.occluded = occluded
        self.outside = outside
        self.source = source
        self.xbl1 = xbl1
        self.xbl2 = xbl2
        self.xbr1 = xbr1
        self.xbr2 = xbr2
        self.xtl1 = xtl1
        self.xtl2 = xtl2
        self.xtr1 = xtr1
        self.xtr2 = xtr2
        self.ybl1 = ybl1
        self.ybl2 = ybl2
        self.ybr1 = ybr1
        self.ybr2 = ybr2
        self.ytl1 = ytl1
        self.ytl2 = ytl2
        self.ytr1 = ytr1
        self.ytr2 = ytr2
        self.z_order = z_order
        self.attribs = attribs
        self.track_id: Optional[int] = None

        for attrib in self.attribs:
            if attrib.name == 'trackId':
                if attrib.value is not None:
                    self.track_id = int(attrib.value)
                    break

    @classmethod
    def parse(cls, instance: ET.Element) -> Instance:
        if instance.tag != cls.tag:
            raise RuntimeError(f'Incompatitable tag, {cls.tag} required, {instance.tag} found.')
        frame = int(instance.attrib['frame'])
        keyframe = int(instance.attrib['keyframe'])
        label = instance.attrib['label']
        occluded = int(instance.attrib['occluded'])
        outside = int(instance.attrib['outside'])
        source = instance.attrib['source']
        xbl1 = float(instance.attrib['xbl1'])
        xbl2 = float(instance.attrib['xbl2'])
        xbr1 = float(instance.attrib['xbr1'])
        xbr2 = float(instance.attrib['xbr2'])
        xtl1 = float(instance.attrib['xtl1'])
        xtl2 = float(instance.attrib['xtl2'])
        xtr1 = float(instance.attrib['xtr1'])
        xtr2 = float(instance.attrib['xtr2'])
        ybl1 = float(instance.attrib['ybl1'])
        ybl2 = float(instance.attrib['ybl2'])
        ybr1 = float(instance.attrib['ybr1'])
        ybr2 = float(instance.attrib['ybr2'])
        ytl1 = float(instance.attrib['ytl1'])
        ytl2 = float(instance.attrib['ytl2'])
        ytr1 = float(instance.attrib['ytr1'])
        ytr2 = float(instance.attrib['ytr2'])
        z_order = int(instance.attrib['z_order'])
        attribs = [Attrib.parse(attrib) for attrib in instance]
        return cls(frame, keyframe, label, occluded, outside, source,
                   xbl1, xbl2, xbr1, xbr2, xtl1, xtl2, xtr1, xtr2,
                   ybl1, ybl2, ybr1, ybr2, ytl1, ytl2, ytr1, ytr2, z_order, attribs)

    @property
    def xml(self) -> ET.Element:
        attrib = {
            'frame': str(self.frame),
            'keyframe': str(self.keyframe),
            'label': str(self.label),
            'occluded': str(self.occluded),
            'outside': str(self.outside),
            'source': str(self.source),
            'xbl1': str(self.xbl1),
            'xbl2': str(self.xbl2),
            'xbr1': str(self.xbr1),
            'xbr2': str(self.xbr2),
            'xtl1': str(self.xtl1),
            'xtl2': str(self.xtl2),
            'xtr1': str(self.xtr1),
            'xtr2': str(self.xtr2),
            'ybl1': str(self.ybl1),
            'ybl2': str(self.ybl2),
            'ybr1': str(self.ybr1),
            'ybr2': str(self.ybr2),
            'ytl1': str(self.ytl1),
            'ytl2': str(self.ytl2),
            'ytr1': str(self.ytr1),
            'ytr2': str(self.ytr2),
            'z_order': str(self.z_order),
        }
        ele = ET.Element(self.tag, attrib)
        ele.extend([attrib.xml for attrib in self.attribs])
        return ele

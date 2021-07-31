from __future__ import annotations

from .base import Element


class Instance(Element):
    def __init__(self, class_: str, width: float, length: float, height: float, x: float, y: float, z: float,
                 rotationY: float, trackId: int, frameIdx: int, score: float = None, prelabel: bool = None):
        super(Instance, self).__init__()
        self.class_ = class_
        self.width = width
        self.length = length
        self.height = height
        self.x = x
        self.y = y
        self.z = z
        self.rotationY = rotationY
        self.trackId = trackId
        self.frameIdx = frameIdx
        self.score = score
        self.prelabel = prelabel

    @classmethod
    def parse(cls, instance: dict) -> Instance:
        class_ = instance['class']
        width = instance['width']
        height = instance['height']
        length = instance['length']
        x = instance['x']
        y = instance['y']
        z = instance['z']
        rotationY = instance['rotationY']
        trackId = instance['trackId']
        frameIdx = instance['frameIdx']
        prelabel = instance.get('prelabel')

        height, length = length, height  # height and length are swapped when being dumped

        return cls(class_, width, length, height, x, y, z, rotationY, trackId, frameIdx, prelabel=prelabel)

    @property
    def json(self) -> dict:

        obj = {
            'class': self.class_,
            'width': self.width,
            'length': self.height,  # swap height and length
            'height': self.length,
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'rotationY': self.rotationY,
            'trackId': self.trackId,
            'frameIdx': self.frameIdx,
        }

        if self.prelabel is not None:
            obj['prelabel'] = self.prelabel

        return obj

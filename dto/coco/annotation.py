from __future__ import annotations

from typing import List

from .base import Element


class BBox(Element):
    def __init__(self, left: float, top: float, width: float, height: float):
        super(BBox, self).__init__()
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    @classmethod
    def parse(cls, bbox: List[float]) -> BBox:
        left, top, width, height = bbox
        return cls(left, top, width, height)

    @property
    def json(self) -> List[float]:
        bbox = [self.left, self.top, self.width, self.height]
        return bbox


class Annotation(Element):
    cnt = 0

    def __init__(self, segmentation: List[List[int]], area: float, iscrowd: int, image_id: int, bbox: BBox,
                 category_id: int, id_: int):
        super(Annotation, self).__init__()
        self.segmentation = segmentation
        self.area = area
        self.iscrowd = iscrowd
        self.image_id = image_id
        self.bbox = bbox
        self.category_id = category_id
        self.id = id_

    @classmethod
    def parse(cls, annotation: dict) -> Annotation:
        segmentation = annotation['segmentation']
        area = annotation['area']
        iscrowd = annotation['iscrowd']
        image_id = annotation['image_id']
        bbox = BBox.parse(annotation['bbox'])
        category_id = annotation['category_id']
        id_ = annotation['id']
        return cls(segmentation, area, iscrowd, image_id, bbox, category_id, id_)

    @property
    def json(self) -> dict:
        annotation = {
            'segmentation': self.segmentation,
            'area': self.area,
            'iscrowd': self.iscrowd,
            'image_id': self.image_id,
            'bbox': self.bbox.json,
            'category_id': self.category_id,
            'id': self.id,
        }
        return annotation

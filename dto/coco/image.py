from __future__ import annotations

from .base import Element


class Image(Element):
    cnt = 0

    def __init__(self, license: int, file_name: str, coco_url: str, height: int, width: int, date_captured: str,
                 flickr_url: str, id_: int):
        super(Image, self).__init__()
        self.license = license
        self.file_name = file_name
        self.coco_url = coco_url
        self.height = height
        self.width = width
        self.date_captured = date_captured
        self.flickr_url = flickr_url
        self.id = id_

    @classmethod
    def parse(cls, image: dict) -> Image:
        license = image['license']
        file_name = image['file_name']
        coco_url = image['coco_url']
        height = image['height']
        width = image['width']
        date_captured = image['date_captured']
        flickr_url = image['flickr_url']
        id_ = image['id']
        return cls(license, file_name, coco_url, height, width, date_captured, flickr_url, id_)

    @property
    def json(self) -> dict:
        image = {
            'license': self.license,
            'file_name': self.file_name,
            'coco_url': self.coco_url,
            'height': self.height,
            'width': self.width,
            'date_captured': self.date_captured,
            'flickr_url': self.flickr_url,
            'id': self.id,
        }
        return image

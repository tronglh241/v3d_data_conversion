from __future__ import annotations

import json
from typing import List

from utils.common import open_file

from .annotation import Annotation
from .base import Element
from .category import Category
from .image import Image
from .info import Info
from .license import License


class Label(Element):
    def __init__(self, info: Info, licenses: List[License], images: List[Image], annotations: List[Annotation],
                 categories: List[Category]):
        super(Label, self).__init__()
        self.info = info
        self.licenses = licenses
        self.images = images
        self.annotations = annotations
        self.categories = categories

    @classmethod
    def parse(cls, label: dict) -> Label:
        info = Info.parse(label['info'])
        licenses = [License.parse(license) for license in label['licenses']]
        images = [Image.parse(image) for image in label['images']]
        annotations = [Annotation.parse(annotation) for annotation in label['annotations']]
        categories = [Category.parse(category) for category in label['categories']]
        return cls(info, licenses, images, annotations, categories)

    @property
    def json(self) -> dict:
        label = {
            'info': self.info.json,
            'licenses': [license.json for license in self.licenses],
            'images': [image.json for image in self.images],
            'annotations': [annotation.json for annotation in self.annotations],
            'categories': [category.json for category in self.categories],
        }
        return label

    @classmethod
    def fromfile(cls, file_path: str) -> Label:
        with open(file_path, mode='r', encoding='utf-8') as f:
            label = json.load(f)

        return cls.parse(label)

    def tofile(self, file_path: str) -> None:
        with open_file(file_path, mode='w', encoding='utf-8') as f:
            json.dump(self.json, f, indent=4)

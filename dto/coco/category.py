from __future__ import annotations

from .base import Element


class Category(Element):
    def __init__(self, supercategory: str, id_: int, name: str):
        super(Category, self).__init__()
        self.supercategory = supercategory
        self.id = id_
        self.name = name

    @classmethod
    def parse(cls, category: dict) -> Category:
        supercategory = category['supercategory']
        id_ = category['id']
        name = category['name']
        return cls(supercategory, id_, name)

    @property
    def json(self) -> dict:
        category = {
            'supercategory': self.supercategory,
            'id': self.id,
            'name': self.name,
        }
        return category

from __future__ import annotations

from .base import Element


class License(Element):
    def __init__(self, url: str, id_: int, name: str):
        super(License, self).__init__()
        self.url = url
        self.id = id_
        self.name = name

    @classmethod
    def parse(cls, license: dict) -> License:
        url = license['url']
        id_ = license['id']
        name = license['name']
        return cls(url, id_, name)

    @property
    def json(self) -> dict:
        license = {
            'url': self.url,
            'id': self.id,
            'name': self.name,
        }
        return license

from __future__ import annotations

from .base import Element


class Info(Element):
    def __init__(self, description: str, url: str, version: str, year: int, contributor: str, date_created: str):
        super(Info, self).__init__()
        self.description = description
        self.url = url
        self.version = version
        self.year = year
        self.contributor = contributor
        self.date_created = date_created

    @classmethod
    def parse(cls, info: dict) -> Info:
        description = info['description']
        url = info['url']
        version = info['version']
        year = info['year']
        contributor = info['contributor']
        date_created = info['date_created']
        return cls(description, url, version, year, contributor, date_created)

    @property
    def json(self) -> dict:
        info = {
            'description': self.description,
            'url': self.url,
            'version': self.version,
            'year': self.year,
            'contributor': self.contributor,
            'date_created': self.date_created,
        }
        return info

from __future__ import annotations

from abc import abstractclassmethod
from typing import Any

from abstract.dto import DTO


class Element(DTO):
    @abstractclassmethod
    def parse(cls, obj: Any) -> Element:
        pass

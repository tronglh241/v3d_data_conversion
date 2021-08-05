from __future__ import annotations

import xml.etree.ElementTree as ET
from abc import abstractproperty
from typing import Optional

from abstract.dto import DTO


class Element(DTO):
    tag: Optional[str] = None

    @classmethod
    def parse(cls, obj: ET.Element) -> Element:
        pass

    @abstractproperty
    def xml(self) -> ET.Element:
        pass

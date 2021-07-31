from __future__ import annotations

from pathlib import Path
from typing import List

from utils.common import open_file

from .base import Element
from .instance import Instance


class Frame(Element):
    def __init__(self, frame_id: int, instances: List[Instance], frame_file: str = None):
        super(Frame, self).__init__()
        self.frame_id = frame_id
        self.instances = instances
        self.frame_file = frame_file

    @property
    def name(self) -> str:
        return f'{self.frame_id:06d}.txt'

    @classmethod
    def parse(cls, frame_file: str) -> Frame:
        with open(frame_file, mode='r', encoding='utf-8') as f:
            instances = [Instance.parse(line) for line in f]

        frame_id = int(Path(frame_file).stem)
        return cls(frame_id, instances)

    def tofile(self, anno_dir: str) -> None:
        frame_file = str(Path(anno_dir).joinpath(self.name))
        with open_file(frame_file, mode='w', encoding='utf-8') as f:
            lines = [f'{instance.txt}\n' for instance in self.instances]

            dontcares = [line for line in lines if line.startswith('DontCare')]
            not_dontcares = [line for line in lines if not line.startswith('DontCare')]

            lines = not_dontcares + dontcares
            f.writelines(lines)

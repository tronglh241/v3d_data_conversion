import shutil
from pathlib import Path
from typing import List, Tuple

from abstract.stage import Stage
from dto.seq.seq_info import SeqInfo


class RmDir(Stage):
    def __init__(self, rm_dirs: List[str]):
        super(RmDir, self).__init__()
        self.rm_dirs = rm_dirs

    def preprocess(self, seq_info: SeqInfo) -> Tuple[SeqInfo]:
        out_dir = Path(seq_info.out_dir).joinpath(seq_info.seq_name)

        for rm_dir in self.rm_dirs:
            shutil.rmtree(str(out_dir.joinpath(rm_dir)), ignore_errors=True)

        return seq_info,

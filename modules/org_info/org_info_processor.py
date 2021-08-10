from pathlib import Path
from typing import Tuple

from abstract.processor import Processor
from dto.seq.seq_info import SeqInfo
from utils.common import open_file


class OrgInfoProcessor(Processor):
    def __init__(self, org_info_dir: str = 'org_info') -> None:
        self.org_info_dir = org_info_dir

    def process(self, seq_info: SeqInfo) -> Tuple[SeqInfo]:
        out_dir = Path(seq_info.out_dir).joinpath(seq_info.seq_name, self.org_info_dir)
        assert seq_info.frame_infos is not None

        for frame_info in seq_info.frame_infos:
            lines = [f'{key}: {value}\n' for key, value in frame_info.asdict().items()]
            frame_org_file = str(out_dir.joinpath(f'{frame_info.frame_name}.txt'))

            with open_file(frame_org_file, mode='w', encoding='utf-8') as f:
                f.writelines(lines)

        return seq_info,

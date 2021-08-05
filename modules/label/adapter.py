from pathlib import Path
from typing import Tuple

from abstract.adapter import InAdapter as InAdapter
from dto.bat3d.label import Label as BAT3DLabel
from dto.cvat.label import Label as CVATLabel
from dto.scale_ai.label import Label as ScaleAILabel
from dto.seq.seq_info import SeqInfo
from utils.common import get_file_with_stem


class BAT3DInAdapter(InAdapter):
    def __init__(self, label_dir: str, label_stem: str):
        super(BAT3DInAdapter, self).__init__()
        self.label_dir = label_dir
        self.label_stem = label_stem

    def convert(self, stage_input: Tuple[SeqInfo]) -> Tuple[SeqInfo, BAT3DLabel]:
        seq_info = stage_input[0]
        label_dir = Path(seq_info.seq_dir).joinpath(self.label_dir)
        label_file = get_file_with_stem(str(label_dir), self.label_stem)

        if label_file is None:
            raise FileNotFoundError('Annotation file not found.')

        label = BAT3DLabel.fromfile(label_file)
        return seq_info, label


class ScaleAIInAdapter(InAdapter):
    def __init__(self, label_dir: str, label_stem: str):
        super(ScaleAIInAdapter, self).__init__()
        self.label_dir = label_dir
        self.label_stem = label_stem

    def convert(self, stage_input: Tuple[SeqInfo]) -> Tuple[SeqInfo, ScaleAILabel]:
        seq_info = stage_input[0]
        label_dir = Path(seq_info.seq_dir).joinpath(self.label_dir)
        label_file = get_file_with_stem(str(label_dir), self.label_stem)

        if label_file is None:
            raise FileNotFoundError('Annotation file not found.')

        label = ScaleAILabel.fromfile(label_file)
        return seq_info, label


class CVATInAdapter(InAdapter):
    def __init__(self, label_dir: str, label_stem: str):
        super(CVATInAdapter, self).__init__()
        self.label_dir = label_dir
        self.label_stem = label_stem

    def convert(self, stage_input: Tuple[SeqInfo]) -> Tuple[SeqInfo, CVATLabel]:
        seq_info = stage_input[0]
        label_dir = Path(seq_info.seq_dir).joinpath(self.label_dir)
        label_file = get_file_with_stem(str(label_dir), self.label_stem)

        if label_file is None:
            raise FileNotFoundError('Annotation file not found.')

        label = CVATLabel.fromfile(label_file)
        return seq_info, label

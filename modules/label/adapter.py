from pathlib import Path
from typing import Tuple

from abstract.adapter import InAdapter as InAdapter
from dto.bat3d.frame import Frame as BAT3DFrame
from dto.bat3d.label import Label as BAT3DLabel
from dto.scale_ai.label import Label as ScaleAILabel
from dto.seq.seq_info import SeqInfo
from utils.common import get_file_with_stem
from utils.instance_converter import scale_ai_to_bat3d


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

    def convert(self, stage_input: Tuple[SeqInfo]) -> Tuple[SeqInfo, BAT3DLabel]:
        seq_info = stage_input[0]
        label_dir = Path(seq_info.seq_dir).joinpath(self.label_dir)
        label_file = get_file_with_stem(str(label_dir), self.label_stem)

        if label_file is None:
            raise FileNotFoundError('Annotation file not found.')

        label = ScaleAILabel.fromfile(label_file)
        bat3d_frames = []
        for frame in label.frames:
            bat3d_instances = [scale_ai_to_bat3d(instance, i, frame.frame_id)
                               for i, instance in enumerate(frame.instances)]
            bat3d_frames.append(BAT3DFrame(frame.frame_id, bat3d_instances))
        bat3d_label = BAT3DLabel(bat3d_frames)
        return seq_info, bat3d_label

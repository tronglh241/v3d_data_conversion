from typing import Any, Tuple

from abstract.stage import Stage
from dto.seq.seq_info import SeqInfo


class Label(Stage):
    def preprocess(self, seq_info: SeqInfo, label: Any, label_file: str) -> Tuple[SeqInfo, Any]:
        frame_names = seq_info.frame_names

        if frame_names is not None:
            for frame_name in frame_names:
                seq_info.set_frame_info(frame_name, label_file=label_file)

        return seq_info, label

from pathlib import Path
from typing import Dict, Tuple

import cv2

from abstract.adapter import InAdapter as InAdapter
from abstract.adapter import OutAdapter
from dto.bat3d.label import Label as BAT3DLabel
from dto.seq.seq_info import SeqInfo
from utils.common import get_file_with_stem, open_file
from utils.instance_converter import bat3d_to_kitti


class BAT3DInAdapter(InAdapter):
    def __init__(self, label_dir: str, label_stem: str):
        self.label_dir = label_dir
        self.label_stem = label_stem

    def convert(self, stage_input: Tuple[SeqInfo]) -> Tuple[BAT3DLabel]:
        seq_info = stage_input[0]
        label_dir = Path(seq_info.seq_dir).joinpath(self.label_dir)
        label_file = get_file_with_stem(str(label_dir), self.label_stem)

        if label_file is None:
            raise FileNotFoundError('Annotation file not found.')

        label = BAT3DLabel.fromfile(label_file)
        return label,


class YOLOTianxiaomoOutAdapter(OutAdapter):
    def __init__(self, label_filename: str, image_dir: str, class_id: Dict[str, int]):
        self.label_filename = label_filename
        self.image_dir = image_dir
        self.class_id = class_id

    def convert(self, stage_input: Tuple[SeqInfo], stage_output: Tuple[BAT3DLabel]) -> Tuple[SeqInfo]:
        seq_info = stage_input[0]
        label = stage_output[0]
        label_file = str(Path(seq_info.out_dir).joinpath(seq_info.seq_name, self.label_filename))
        image_dir = str(Path(seq_info.seq_dir).joinpath(self.image_dir))

        extrinsic = seq_info.extrinsic
        intrinsic = seq_info.intrinsic
        assert extrinsic is not None
        assert intrinsic is not None

        with open_file(label_file, mode='w', encoding='utf-8') as f:
            for frame in label.frames:
                if frame.instances:
                    image_file = get_file_with_stem(image_dir, frame.name)

                    if image_file is None:
                        raise FileNotFoundError('Image file not found.')

                    width, height = cv2.imread(image_file).shape[1::-1]
                    kitti_instances = [bat3d_to_kitti(instance, extrinsic, intrinsic, (width, height))
                                       for instance in frame.instances]
                    instances = [(*instance.bbox, self.class_id[instance.type]) for instance in kitti_instances
                                 if instance.type in self.class_id]
                    instances = list(filter(lambda instance: all(map(lambda x: x >= 0, instance)), instances))

                    if instances:
                        line = f'{image_file} {" ".join(map(lambda x: str(x), instances))}\n'
                        f.write(line)

        return seq_info,

from pathlib import Path
from typing import Dict, Tuple

import cv2

from abstract.adapter import InAdapter as InAdapter
from abstract.adapter import OutAdapter
from dto.bat3d.frame import Frame as BAT3DFrame
from dto.bat3d.label import Label as BAT3DLabel
from dto.scale_ai.label import Label as ScaleAILabel
from dto.seq.seq_info import SeqInfo
from utils.common import get_file_with_stem, open_file
from utils.instance_converter import bat3d_to_kitti, scale_ai_to_bat3d


class BAT3DInAdapter(InAdapter):
    def __init__(self, label_dir: str, label_stem: str):
        super(BAT3DInAdapter, self).__init__()
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


class ScaleAIInAdapter(InAdapter):
    def __init__(self, label_dir: str, label_stem: str):
        super(ScaleAIInAdapter, self).__init__()
        self.label_dir = label_dir
        self.label_stem = label_stem

    def convert(self, stage_input: Tuple[SeqInfo]) -> Tuple[BAT3DLabel]:
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
        return bat3d_label,


class YOLOTianxiaomoOutAdapter(OutAdapter):
    def __init__(self, label_filename: str, image_dir: str, class_id: Dict[str, int], rm_thres: float,
                 rm_box_ratio: float):
        super(YOLOTianxiaomoOutAdapter, self).__init__()
        self.label_filename = label_filename
        self.image_dir = image_dir
        self.class_id = class_id
        self.rm_thres = rm_thres
        self.rm_box_ratio = rm_box_ratio

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

                    if ' ' in str(image_file):
                        raise RuntimeError('Image path contains spaces.')

                    width, height = cv2.imread(image_file).shape[1::-1]
                    kitti_instances = [bat3d_to_kitti(instance, extrinsic, intrinsic, (width, height))
                                       for instance in frame.instances]

                    # Keep classes of interest
                    kitti_instances = list(filter(lambda instance: instance.type in self.class_id, kitti_instances))
                    # Keep bboxes in the image
                    kitti_instances = list(filter(lambda instance: all(map(lambda x: x >= 0, instance.bbox)),
                                                  kitti_instances))
                    kitti_instances = list(filter(lambda instance: (instance.bbox[2] - instance.bbox[0])
                                                  / (instance.bbox[3] - instance.bbox[1]) > self.rm_box_ratio,
                                                  kitti_instances))
                    # Sort by distance from camera
                    kitti_instances.sort(key=lambda instance: instance.location[2], reverse=True)

                    rm_instances = []
                    for i, instance1 in enumerate(kitti_instances):
                        for instance2 in kitti_instances[i + 1:]:
                            xA = max(instance1.bbox[0], instance2.bbox[0])
                            yA = max(instance1.bbox[1], instance2.bbox[1])
                            xB = min(instance1.bbox[2], instance2.bbox[2])
                            yB = min(instance1.bbox[3], instance2.bbox[3])

                            interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
                            boxAArea = ((instance1.bbox[2] - instance1.bbox[0] + 1)
                                        * (instance1.bbox[3] - instance1.bbox[1] + 1))

                            if interArea / boxAArea > self.rm_thres:
                                rm_instances.append(instance1)
                                break

                    for instance in rm_instances:
                        kitti_instances.remove(instance)

                    instances = [(*instance.bbox, self.class_id[instance.type]) for instance in kitti_instances]

                    if instances:
                        boxes = [str(ele) for instance in instances for ele in instance]
                        line = image_file + ' ' + ' '.join(boxes) + '\n'
                        f.write(line)

        return seq_info,

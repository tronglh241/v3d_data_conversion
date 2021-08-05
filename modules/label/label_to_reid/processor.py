from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2

from abstract.processor import Processor
from dto.bat3d.frame import Frame as BAT3DFrame
from dto.bat3d.label import Label as BAT3DLabel
from dto.box.box2d import Box2D
from dto.scale_ai.label import Label as ScaleAILabel
from dto.seq.seq_info import SeqInfo
from utils.common import get_file_with_stem
from utils.instance_converter import bat3d_to_kitti, scale_ai_to_bat3d


class LabelProcessor(Processor):
    def __init__(self, classes_id: Dict[str, int], image_dir: str, rm_thres: float, rm_box_ratio: float):
        super(LabelProcessor, self).__init__()
        self.classes_id = classes_id
        self.image_dir = image_dir
        self.rm_thres = rm_thres
        self.rm_box_ratio = rm_box_ratio

    def preprocess(self, seq_info: SeqInfo, label: Any) -> Tuple[SeqInfo, List[str], List[List[Box2D]]]:
        image_dir = str(Path(seq_info.seq_dir).joinpath(self.image_dir))
        extrinsic = seq_info.extrinsic
        intrinsic = seq_info.intrinsic
        assert extrinsic is not None
        assert intrinsic is not None

        image_files: List[str] = []
        frames: List[List[Box2D]] = []

        if isinstance(label, (BAT3DLabel, ScaleAILabel)):
            if isinstance(label, ScaleAILabel):
                bat3d_frames = []
                for frame in label.frames:
                    bat3d_instances = [scale_ai_to_bat3d(ins, track_id, frame.frame_id)
                                       for track_id, ins in enumerate(frame.instances)]
                    bat3d_frame = BAT3DFrame(frame.frame_id, bat3d_instances)
                    bat3d_frames.append(bat3d_frame)
                label = BAT3DLabel(bat3d_frames)

            for bat3d_frame in label.frames:
                image_file = get_file_with_stem(image_dir, bat3d_frame.name)

                if image_file is None:
                    raise FileNotFoundError(f'{bat3d_frame.name} not found.')

                if ' ' in str(image_file):
                    raise RuntimeError('image_file contains spaces.')

                height, width, _ = cv2.imread(image_file).shape
                kitti_instances = [bat3d_to_kitti(instance, extrinsic, intrinsic, (width, height))
                                   for instance in bat3d_frame.instances]
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

                if kitti_instances:
                    image_files.append(image_file)
                    boxes = [Box2D(int(ins.bbox[0]), int(ins.bbox[1]), int(ins.bbox[2]), int(ins.bbox[3]), ins.type,
                                   ins.track_id) for ins in kitti_instances]
                    frames.append(boxes)
        else:
            raise TypeError('Not handled type.')

        return seq_info, image_files, frames

    def process(self, seq_info: SeqInfo, image_files: List[str], frames: List[List[Box2D]]) -> Tuple[SeqInfo]:
        out_dir = Path(seq_info.out_dir)
        seq_name = Path(seq_info.seq_dir).name
        for image_file, boxes in zip(image_files, frames):
            image = cv2.imread(image_file)
            boxes = list(filter(lambda box: box.type in self.classes_id, boxes))
            if boxes:
                for box in boxes:
                    if box.track_id is not None:
                        instance_img = image[box.top:box.bottom, box.left:box.right]
                        instance_file = out_dir.joinpath('_'.join([seq_name, box.type, str(box.track_id)]),
                                                         '_'.join(Path(image_file).parts[-2:]))
                        instance_file.parent.mkdir(parents=True, exist_ok=True)
                        cv2.imwrite(str(instance_file), instance_img)
        return seq_info,

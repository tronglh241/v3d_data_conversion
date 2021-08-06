from pathlib import Path
from typing import Any, List, Tuple

import cv2

from abstract.processor import Processor
from dto.bat3d.frame import Frame as BAT3DFrame
from dto.bat3d.label import Label as BAT3DLabel
from dto.box.box2d import Box2D
from dto.cvat.label import Label as CVATLabel
from dto.scale_ai.label import Label as ScaleAILabel
from dto.seq.seq_info import SeqInfo
from utils.common import get_file_with_stem
from utils.instance_converter import bat3d_to_kitti, scale_ai_to_bat3d


class LabelProcessor(Processor):
    def __init__(self, image_dir: str, rm_thres: float, rm_box_ratio: float):
        super(LabelProcessor, self).__init__()
        self.image_dir = image_dir
        self.rm_thres = rm_thres
        self.rm_box_ratio = rm_box_ratio

    def process(self, seq_info: SeqInfo, label: Any) -> Tuple[SeqInfo, List[str], List[List[Box2D]]]:
        image_dir = Path(seq_info.seq_dir).joinpath(self.image_dir)

        image_files: List[str] = []
        frames: List[List[Box2D]] = []

        if isinstance(label, (BAT3DLabel, ScaleAILabel)):
            extrinsic = seq_info.extrinsic
            intrinsic = seq_info.intrinsic
            assert extrinsic is not None
            assert intrinsic is not None

            if isinstance(label, ScaleAILabel):
                bat3d_frames = []
                for frame in label.frames:
                    bat3d_instances = [scale_ai_to_bat3d(ins, track_id, frame.frame_id)
                                       for track_id, ins in enumerate(frame.instances)]
                    bat3d_frame = BAT3DFrame(frame.frame_id, bat3d_instances)
                    bat3d_frames.append(bat3d_frame)
                label = BAT3DLabel(bat3d_frames)

            for bat3d_frame in label.frames:
                image_file = get_file_with_stem(str(image_dir), bat3d_frame.name)

                if image_file is None:
                    raise FileNotFoundError(f'{bat3d_frame.name} not found.')

                if ' ' in str(image_file):
                    raise RuntimeError('image_file contains spaces.')

                height, width, _ = cv2.imread(image_file).shape
                kitti_instances = [bat3d_to_kitti(instance, extrinsic, intrinsic, (width, height))
                                   for instance in bat3d_frame.instances]

                # Sort by distance from camera
                kitti_instances.sort(key=lambda instance: instance.location[2], reverse=True)

                if kitti_instances:
                    image_files.append(image_file)
                    boxes = [Box2D(int(ins.bbox[0]), int(ins.bbox[1]), int(ins.bbox[2]), int(ins.bbox[3]), ins.type,
                                   ins.track_id) for ins in kitti_instances]
                    frames.append(boxes)
        elif isinstance(label, CVATLabel):
            for cvat_frame in label.frames:
                image_file = str(image_dir.joinpath(cvat_frame.name).resolve())
                height, width, _ = cv2.imread(image_file).shape
                image_files.append(image_file)
                boxes = []
                for cvat_instance in cvat_frame.instances:
                    xs = [cvat_instance.xbl1, cvat_instance.xbl2, cvat_instance.xbr1, cvat_instance.xbr2,
                          cvat_instance.xtl1, cvat_instance.xtl2, cvat_instance.xtr1, cvat_instance.xtr2]
                    ys = [cvat_instance.ybl1, cvat_instance.ybl2, cvat_instance.ybr1, cvat_instance.ybr2,
                          cvat_instance.ytl1, cvat_instance.ytl2, cvat_instance.ytr1, cvat_instance.ytr2]
                    left = max(round(min(xs)), 0)
                    right = min(round(max(xs)), width)
                    top = max(round(min(ys)), 0)
                    bottom = min(round(max(ys)), height)
                    type_ = cvat_instance.label
                    track_id = cvat_instance.track_id
                    boxes.append(Box2D(left, top, right, bottom, type_, track_id))
                boxes.sort(key=lambda box: (box.right - box.left) * (box.bottom - box.top))
                frames.append(boxes)
        else:
            raise TypeError('Not handled type.')

        for image_file, boxes in zip(image_files, frames):
            rm_boxes = []
            for box in boxes:
                if box.bottom == box.top or (box.right - box.left) / (box.bottom - box.top) < self.rm_box_ratio:
                    rm_boxes.append(box)
            for box in rm_boxes:
                boxes.remove(box)

        for image_file, boxes in zip(image_files, frames):
            rm_boxes = []
            for i, box1 in enumerate(boxes):
                for box2 in boxes[i + 1:]:
                    xA = max(box1.left, box2.left)
                    yA = max(box1.top, box2.top)
                    xB = min(box1.right, box2.right)
                    yB = min(box1.bottom, box2.bottom)

                    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
                    boxAArea = ((box1.right - box1.left + 1)
                                * (box1.bottom - box1.top + 1))

                    if interArea / boxAArea > self.rm_thres:
                        rm_boxes.append(box1)
                        break
            for box in rm_boxes:
                boxes.remove(box)

        return seq_info, image_files, frames

from typing import Tuple, Union

from abstract.processor import Processor
from dto.bat3d.frame import Frame as BAT3DFrame
from dto.bat3d.label import Label as BAT3DLabel
from dto.kitti.label.frame import Frame as KITTIFrame
from dto.kitti.label.label import Label as KITTILabel
from dto.scale_ai.label import Label as ScaleAILabel
from dto.seq.seq_info import SeqInfo
from utils.instance_converter import bat3d_to_kitti, scale_ai_to_bat3d


class LabelProcessor(Processor):
    def __init__(self, image_size: Tuple[int, int] = None, padding: bool = False):
        super(LabelProcessor, self).__init__()
        self.image_size = image_size
        self.padding = padding

    def preprocess(self, seq_info: SeqInfo, label: Union[BAT3DLabel, ScaleAILabel]) -> Tuple[SeqInfo, KITTILabel]:
        kitti_frames = []
        extrinsic = seq_info.extrinsic
        intrinsic = seq_info.intrinsic
        image_size = seq_info.image_size
        assert extrinsic is not None
        assert intrinsic is not None
        assert image_size is not None

        if isinstance(label, ScaleAILabel):
            bat3d_frames = []
            for frame in label.frames:
                bat3d_instances = [scale_ai_to_bat3d(instance, track_id, frame.frame_id)
                                   for track_id, instance in enumerate(frame.instances)]
                bat3d_frame = BAT3DFrame(frame.frame_id, bat3d_instances)
                bat3d_frames.append(bat3d_frame)
            label = BAT3DLabel(bat3d_frames)

        for bat3d_frame in label.frames:
            kitti_instances = [bat3d_to_kitti(instance, extrinsic, intrinsic, image_size)
                               for instance in bat3d_frame.instances]
            kitti_frame = KITTIFrame(bat3d_frame.frame_id, kitti_instances)
            kitti_frames.append(kitti_frame)
        kitti_label = KITTILabel(kitti_frames)
        return seq_info, kitti_label

    def process(self, seq_info: SeqInfo, label: KITTILabel) -> Tuple[SeqInfo, KITTILabel]:
        org_image_size = seq_info.image_size
        assert org_image_size is not None

        if self.image_size is not None:
            for frame in label.frames:
                self.pad_resize_bbox(frame, org_image_size)

        return seq_info, label

    def pad_resize_bbox(self, frame: KITTIFrame, org_image_size: Tuple[int, int]) -> KITTIFrame:
        assert self.image_size is not None
        for instance in frame.instances:
            width, height = org_image_size

            if self.padding:
                scale_x = scale_y = min(self.image_size[0] / width, self.image_size[1] / height)
            else:
                scale_x = self.image_size[0] / width
                scale_y = self.image_size[1] / height

            left, top, right, bottom = instance.bbox
            instance.bbox = (left * scale_x, top * scale_y, right * scale_x, bottom * scale_y)
        return frame

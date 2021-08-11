from pathlib import Path
from typing import List, Tuple

from abstract.processor import Processor
from dto.kitti.label.frame import Frame as KITTIFrame
from dto.kitti.label.label import Label as KITTILabel
from dto.pred.box3d import LiDARBox3D
from dto.seq.seq_info import SeqInfo
from utils.instance_converter import lidar_box3d_to_kitti


class KITTIProcessor(Processor):
    def __init__(self, label_dir: str = 'label_2'):
        super(KITTIProcessor, self).__init__()
        self.label_dir = label_dir

    def process(self, seq_info: SeqInfo, frames: List[List[LiDARBox3D]]) -> Tuple[SeqInfo]:
        out_dir = Path(seq_info.out_dir).joinpath(seq_info.seq_name, self.label_dir)
        extrinsic = seq_info.extrinsic
        intrinsic = seq_info.calib_intrinsic
        image_size = seq_info.resized_image_size
        frame_names = seq_info.frame_names
        assert image_size is not None
        assert frame_names is not None
        assert extrinsic is not None
        assert intrinsic is not None

        kitti_frames = []
        for frame_name, frame in zip(frame_names, frames):
            kitti_instances = [lidar_box3d_to_kitti(lidar_box3d, extrinsic, intrinsic, image_size)
                               for lidar_box3d in frame]
            kitti_frame = KITTIFrame(int(frame_name), kitti_instances)
            kitti_frames.append(kitti_frame)
        label_2 = KITTILabel(kitti_frames)
        label_2.tofile(str(out_dir))

        return seq_info,

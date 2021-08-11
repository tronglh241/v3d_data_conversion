from pathlib import Path
from typing import List, Tuple

from abstract.processor import Processor
from dto.bat3d.frame import Frame as BAT3DFrame
from dto.bat3d.label import Label as BAT3DLabel
from dto.pred.box3d import LiDARBox3D
from dto.seq.seq_info import SeqInfo
from utils.instance_converter import lidar_box3d_to_bat3d


class BAT3DProcessor(Processor):
    def __init__(self, label_dir: str = 'annotations/LIDAR_TOP', prelabel_attr: bool = False):
        super(BAT3DProcessor, self).__init__()
        self.label_dir = label_dir
        self.prelabel_attr = prelabel_attr

    def process(self, seq_info: SeqInfo, frames: List[List[LiDARBox3D]]) -> Tuple[SeqInfo]:
        out_dir = Path(seq_info.out_dir).joinpath(seq_info.seq_name, self.label_dir)
        frame_names = seq_info.frame_names
        assert frame_names is not None
        prelabel = True if self.prelabel_attr else None

        bat3d_frames = []
        for frame_name, frame in zip(frame_names, frames):
            bat3d_instances = []
            for i, instance in enumerate(frame):
                trackId = i if instance.trackId is None else instance.trackId
                bat3d_instance = lidar_box3d_to_bat3d(instance, trackId, int(frame_name), prelabel)
                bat3d_instances.append(bat3d_instance)
            bat3d_frame = BAT3DFrame(int(frame_name), bat3d_instances)
            bat3d_frames.append(bat3d_frame)
        bat3d_anno = BAT3DLabel(bat3d_frames)
        bat3d_anno.tofile(str(out_dir.joinpath(f'NuScenes_{seq_info.seq_name}_annotations.txt')))

        return seq_info,

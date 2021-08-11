from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np

from abstract.processor import Processor
from dto.kitti.label.frame import Frame as KITTIFrame
from dto.pred.box3d import LiDARBox3D
from dto.seq.seq_info import SeqInfo
from utils.instance_converter import lidar_box3d_to_kitti
from utils.kitti import compute_box_3d
from utils.matrix import homo_mat


class ImageProcessor(Processor):
    def __init__(self, image_dir: str = 'image'):
        super(ImageProcessor, self).__init__()
        self.image_dir = image_dir

    def process(self, seq_info: SeqInfo, frames: List[List[LiDARBox3D]]) -> Tuple[SeqInfo]:
        out_dir = Path(seq_info.out_dir).joinpath(seq_info.seq_name, self.image_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        extrinsic = seq_info.extrinsic
        intrinsic = seq_info.intrinsic
        frame_names = seq_info.frame_names
        assert extrinsic is not None
        assert intrinsic is not None
        assert frame_names is not None

        for frame_name, frame in zip(frame_names, frames):
            frame_info = seq_info.get_frame_info(frame_name)

            if frame_info is not None:
                if frame_info.image_file is not None:
                    image = cv2.imread(frame_info.image_file)

                kitti_instances = [lidar_box3d_to_kitti(lidar_box3d, extrinsic, intrinsic, image.shape[1::-1])
                                   for lidar_box3d in frame]
                kitti_frame = KITTIFrame(int(frame_name), kitti_instances)
                self.visualize(image, kitti_frame, intrinsic, str(out_dir))

        return seq_info,

    def visualize(self, image: np.ndarray, kitti_frame: KITTIFrame, intrinsic: np.ndarray, out_dir: str) -> None:
        image_box2d = image.copy()
        image_box3d = image.copy()

        for kitti_instance in kitti_frame.instances:
            left, top, right, bottom = kitti_instance.bbox
            image_box2d = cv2.rectangle(image_box2d, (left, top), (right, bottom), (0, 255, 0), thickness=2)

            height, width, length = kitti_instance.dimensions
            location = kitti_instance.location
            rotation_y = kitti_instance.rotation_y
            bbox_8points, _ = compute_box_3d(width, height, length, location, rotation_y, homo_mat(intrinsic))

            if bbox_8points is not None:
                image_box3d = self.draw_projected_box3d(image_box3d, bbox_8points, color=(0, 255, 0), thickness=2)

        cv2.imwrite(str(Path(out_dir).joinpath(f'{kitti_frame.name}_2d_box.jpg')), image_box2d)
        cv2.imwrite(str(Path(out_dir).joinpath(f'{kitti_frame.name}_3d_box.jpg')), image_box3d)

    def draw_projected_box3d(self, image: np.ndarray, qs: np.ndarray, color: Tuple[int, int, int],
                             thickness: int) -> np.ndarray:
        """ Draw 3d bounding box in image
            qs: (8,3) array of vertices for the 3d box in following order:
                1 -------- 0
               /|         /|
              2 -------- 3 .
              | |        | |
              . 5 -------- 4
              |/         |/
              6 -------- 7
        """
        qs = qs.astype(np.int32)
        for k in range(0, 4):
            # Ref: http://docs.enthought.com/mayavi/mayavi/auto/mlab_helper_functions.html
            i, j = k, (k + 1) % 4
            # use LINE_AA for opencv3
            # cv2.line(image, (qs[i,0],qs[i,1]), (qs[j,0],qs[j,1]), color, thickness, cv2.CV_AA)
            cv2.line(image, (qs[i, 0], qs[i, 1]), (qs[j, 0], qs[j, 1]), color, thickness)
            i, j = k + 4, (k + 1) % 4 + 4
            cv2.line(image, (qs[i, 0], qs[i, 1]), (qs[j, 0], qs[j, 1]), color, thickness)

            i, j = k, k + 4
            cv2.line(image, (qs[i, 0], qs[i, 1]), (qs[j, 0], qs[j, 1]), color, thickness)
        return image

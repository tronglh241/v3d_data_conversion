from __future__ import annotations

from typing import Tuple

from .base import Element


class Instance(Element):
    def __init__(self, type_: str, truncated: float, occluded: int, bbox: Tuple[float, float, float, float],
                 alpha: float, dimensions: Tuple[float, float, float], location: Tuple[float, float, float],
                 rotation_y: float, score: float = None, track_id: int = None):
        '''
            Args:
                type: Describes the type of object: 'Car', 'Van', 'Truck', 'Pedestrian', 'Person_sitting',
                        'Cyclist', 'Tram', 'Misc' or 'DontCare'
                truncated: Float from 0 (non-truncated) to 1 (truncated), where truncated refers to the object
                        leaving image boundaries
                occluded: Integer (0,1,2,3) indicating occlusion state: 0 = fully visible, 1 = partly occluded
                        2 = largely occluded, 3 = unknown
                alpha: Observation angle of object, ranging [-pi..pi]
                bbox: 2D bounding box of object in the image (0-based index): contains left, top,
                        right, bottom pixel coordinates
                dimensions: 3D object dimensions: height, width, length (in meters)
                location: 3D object location x,y,z in camera coordinates (in meters) (bottom-side center)
                rotation_y: Rotation ry around Y-axis in camera coordinates [-pi..pi]
                score: Only for results: Float, indicating confidence in detection, needed for p/r curves,
                        higher is better.
        '''
        super(Instance, self).__init__()
        self.type = type_
        self.truncated = truncated
        self.occluded = occluded
        self.bbox = bbox
        self.alpha = alpha
        self.dimensions = dimensions
        self.location = location
        self.rotation_y = rotation_y
        self.score = score
        self.track_id = track_id

    @classmethod
    def parse(cls, line: str) -> Instance:
        eles = line.strip().split()
        type_ = eles[0].replace('_', ' ')
        truncated = float(eles[1])
        occluded = int(eles[2])
        alpha = float(eles[3])
        bbox = (float(eles[4]), float(eles[5]), float(eles[6]), float(eles[7]))
        dimensions = (float(eles[8]), float(eles[9]), float(eles[10]))
        location = (float(eles[11]), float(eles[12]), float(eles[13]))
        rotation_y = float(eles[14])
        score = float(eles[15]) if len(eles) == 16 else None
        return cls(type_, truncated, occluded, bbox, alpha, dimensions, location, rotation_y, score)

    @property
    def txt(self) -> str:
        eles = [
            self.type,
            self.truncated,
            self.occluded,
            self.alpha,
            *self.bbox,
            *self.dimensions,
            *self.location,
            self.rotation_y,
        ]

        if self.score is not None:
            eles.append(self.score)

        line = ' '.join([str(ele) for ele in eles])
        return line

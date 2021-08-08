from pathlib import Path
from typing import Dict, List, Tuple

import cv2

from abstract.adapter import InAdapter, OutAdapter
from dto.bat3d.label import Label as BAT3DLabel
from dto.box.box2d import Box2D
from dto.coco.annotation import Annotation as COCOAnnotation
from dto.coco.annotation import BBox as COCOBBox
from dto.coco.category import Category as COCOCategory
from dto.coco.image import Image as COCOImage
from dto.coco.info import Info as COCOInfo
from dto.coco.label import Label as COCOLabel
from dto.coco.license import License as COCOLicense
from dto.cvat.label import Label as CVATLabel
from dto.scale_ai.label import Label as ScaleAILabel
from dto.seq.seq_info import SeqInfo
from utils.common import get_file_with_stem, open_file


class BAT3DInAdapter(InAdapter):
    def __init__(self, label_dir: str, label_stem: str):
        super(BAT3DInAdapter, self).__init__()
        self.label_dir = label_dir
        self.label_stem = label_stem

    def convert(self, stage_input: Tuple[SeqInfo]) -> Tuple[SeqInfo, BAT3DLabel]:
        seq_info = stage_input[0]
        label_dir = Path(seq_info.seq_dir).joinpath(self.label_dir)
        label_file = get_file_with_stem(str(label_dir), self.label_stem)

        if label_file is None:
            raise FileNotFoundError('Annotation file not found.')

        label = BAT3DLabel.fromfile(label_file)
        return seq_info, label


class ScaleAIInAdapter(InAdapter):
    def __init__(self, label_dir: str, label_stem: str):
        super(ScaleAIInAdapter, self).__init__()
        self.label_dir = label_dir
        self.label_stem = label_stem

    def convert(self, stage_input: Tuple[SeqInfo]) -> Tuple[SeqInfo, ScaleAILabel]:
        seq_info = stage_input[0]
        label_dir = Path(seq_info.seq_dir).joinpath(self.label_dir)
        label_file = get_file_with_stem(str(label_dir), self.label_stem)

        if label_file is None:
            raise FileNotFoundError('Annotation file not found.')

        label = ScaleAILabel.fromfile(label_file)
        return seq_info, label


class CVATInAdapter(InAdapter):
    def __init__(self, label_dir: str, label_stem: str):
        super(CVATInAdapter, self).__init__()
        self.label_dir = label_dir
        self.label_stem = label_stem

    def convert(self, stage_input: Tuple[SeqInfo]) -> Tuple[SeqInfo, CVATLabel]:
        seq_info = stage_input[0]
        label_dir = Path(seq_info.seq_dir).joinpath(self.label_dir)
        label_file = get_file_with_stem(str(label_dir), self.label_stem)

        if label_file is None:
            raise FileNotFoundError('Annotation file not found.')

        label = CVATLabel.fromfile(label_file)
        return seq_info, label


class COCOOutAdapter(OutAdapter):
    label_filename = 'label.json'

    def __init__(self, classes_id: Dict[str, int], image_dir: str):
        super(COCOOutAdapter, self).__init__()
        self.classes_id = classes_id
        self.image_dir = image_dir

    def convert(self, stage_input: Tuple[SeqInfo], stage_output: Tuple[SeqInfo, List[str], List[List[Box2D]]]) \
            -> Tuple[SeqInfo]:
        seq_info, image_files, frames = stage_output
        out_dir = Path(seq_info.out_dir)
        image_dir = out_dir.joinpath(seq_info.seq_name, self.image_dir)
        image_dir.mkdir(parents=True, exist_ok=True)
        label_file = out_dir.joinpath(seq_info.seq_name, COCOOutAdapter.label_filename)
        if label_file.exists():
            label = COCOLabel.fromfile(str(label_file))
            images = label.images
            annotations = label.annotations
        else:
            images = []
            annotations = []

        # Info
        description = url = version = contributor = date_created = ''
        year = 2021
        info = COCOInfo(description, url, version, year, contributor, date_created)

        # Licences
        url = name = ''
        id_ = 0
        license = COCOLicense(url, id_, name)
        licenses = [license]

        # Categories
        categories = []
        for name, id_ in self.classes_id.items():
            supercategory = 'object'
            category = COCOCategory(supercategory, id_, name)
            categories.append(category)

        # Images and annotations
        for image_file, boxes in zip(image_files, frames):
            if not boxes:
                continue

            # Image
            if any([box.type in self.classes_id for box in boxes]):
                image_license = 0
                coco_url = date_captured = flickr_url = ''
                id_ = COCOImage.cnt
                file_name = f'{id_:012d}.jpg'
                _image = cv2.imread(image_file)
                cv2.imwrite(str(image_dir.joinpath(file_name)), _image)
                height, width, _ = _image.shape
                image = COCOImage(image_license, file_name, coco_url, height, width, date_captured, flickr_url, id_)
                images.append(image)
                COCOImage.cnt += 1

            # Annotation
            for box in boxes:
                if box.type in self.classes_id:
                    segmentation: List[List[int]] = []
                    bbox = COCOBBox(box.left, box.top, box.right - box.left, box.bottom - box.top)
                    area = bbox.width * bbox.height
                    iscrowd = 0
                    image_id = image.id
                    category_id = self.classes_id[box.type]
                    id_ = COCOAnnotation.cnt
                    annotation = COCOAnnotation(segmentation, area, iscrowd, image_id, bbox, category_id, id_)
                    annotations.append(annotation)
                    COCOAnnotation.cnt += 1

        label = COCOLabel(info, licenses, images, annotations, categories)
        label.tofile(str(label_file))
        return seq_info,


class YOLOOutAdapter(OutAdapter):
    def __init__(self, classes_id: Dict[str, int]):
        super(YOLOOutAdapter, self).__init__()
        self.classes_id = classes_id
        self.image_dir = 'images'
        self.label_dir = 'labels'

    def convert(self, stage_input: Tuple[SeqInfo], stage_output: Tuple[SeqInfo, List[str], List[List[Box2D]]]) \
            -> Tuple[SeqInfo]:
        seq_info, image_files, frames = stage_output
        image_dir = Path(seq_info.out_dir).joinpath(seq_info.seq_name, self.image_dir)
        label_dir = Path(seq_info.out_dir).joinpath(seq_info.seq_name, self.label_dir)
        image_dir.mkdir(parents=True, exist_ok=True)
        for image_file, frame in zip(image_files, frames):
            if any([box.type in self.classes_id for box in frame]):
                seq_name = seq_info.seq_name
                cam_name = Path(image_file).parts[-2]
                image_name = Path(image_file).stem
                file_name = f'{seq_name}_{cam_name}_{image_name}'
                image = cv2.imread(image_file)
                image_width, image_height = image.shape[1::-1]

                cv2.imwrite(str(image_dir.joinpath(f'{file_name}.jpg')), image)

                with open_file(str(label_dir.joinpath(f'{file_name}.txt')), mode='w', encoding='utf-8') as f:
                    for box in frame:
                        if box.type in self.classes_id:
                            type_id = self.classes_id[box.type]
                            center_x = (box.left + box.right) / 2 / image_width
                            center_y = (box.top + box.bottom) / 2 / image_height
                            width = (box.right - box.left) / image_width
                            height = (box.bottom - box.top) / image_height
                            f.write(f'{type_id} {center_x} {center_y} {width} {height}\n')
        return seq_info,


class Market1501OutAdapter(OutAdapter):
    instance_ids: Dict[str, int] = {}

    def __init__(self, classes_id: Dict[str, int], cams_id: Dict[str, int]):
        super(Market1501OutAdapter, self).__init__()
        self.classes_id = classes_id
        self.cams_id = cams_id

    def convert(self, stage_input: Tuple[SeqInfo], stage_output: Tuple[SeqInfo, List[str], List[List[Box2D]]]) \
            -> Tuple[SeqInfo]:
        seq_info, image_files, frames = stage_output
        out_dir = Path(seq_info.out_dir)

        for image_file, frame in zip(image_files, frames):
            if any([box.type in self.classes_id for box in frame]):
                seq_name = seq_info.seq_name
                cam_name = Path(image_file).parts[-2]
                image_name = Path(image_file).stem
                image = cv2.imread(image_file)
                cam_id = self.cams_id[cam_name]

                for box in frame:
                    instance_dirname = f'{seq_name}_{box.type}_{box.track_id}'

                    if instance_dirname not in Market1501OutAdapter.instance_ids:
                        Market1501OutAdapter.instance_ids[instance_dirname] = len(Market1501OutAdapter.instance_ids) + 1

                    instance_id = Market1501OutAdapter.instance_ids[instance_dirname]
                    instance_file = out_dir.joinpath(f'{instance_id:04d}', f'{cam_id:04d}',
                                                     f'{seq_name}_{cam_name}_{image_name}.jpg')
                    instance_file.parent.mkdir(parents=True, exist_ok=True)
                    instance_img = image[box.top:box.bottom, box.left:box.right]
                    cv2.imwrite(str(instance_file), instance_img)
        return seq_info,

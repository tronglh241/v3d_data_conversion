from pathlib import Path
from typing import Iterator, List, Optional, Tuple, Union

import numpy as np
from natsort import natsorted
from pyntcloud import PyntCloud

from abstract.adapter import InAdapter
from dto.seq.seq_info import SeqInfo
from utils.common import get_file_with_stem


class BAT3DInAdapter(InAdapter):
    def __init__(self, pcd_dirs: List[str] = ['pointclouds_org'], pcd_suffix: str = '.pcd',
                 file_id: Union[int, list, tuple] = None) -> None:
        super(BAT3DInAdapter, self).__init__()
        self.pcd_dirs = pcd_dirs
        self.pcd_suffix = pcd_suffix

        if isinstance(file_id, int):
            file_id = [file_id]
        elif isinstance(file_id, tuple):
            file_id = list(range(*file_id))

        self.file_id = file_id

    def convert(self, stage_input: Tuple) -> Tuple[SeqInfo, List[str], List[str], Iterator[np.ndarray]]:
        seq_info = stage_input[0]
        frame_names = seq_info.frame_names

        pcd_dir: Optional[Path] = None
        for dirname in self.pcd_dirs:
            _pcd_dir = Path(seq_info.seq_dir).joinpath(dirname)

            if _pcd_dir.exists():
                pcd_dir = _pcd_dir
                break

        if pcd_dir is None:
            raise RuntimeError(f'Point clouds folder not found in {seq_info.seq_dir}')

        if frame_names is None:
            pcd_files = natsorted(pcd_dir.glob(f'*{self.pcd_suffix}'), key=lambda file: file.stem)

            if self.file_id is not None:
                pcd_files = [pcd_files[i] for i in self.file_id]

            frame_names = [pcd_file.stem for pcd_file in pcd_files]
            pcd_files = [str(pcd_file.resolve()) for pcd_file in pcd_files]
        else:
            files = [get_file_with_stem(str(pcd_dir), frame_name)
                     for frame_name in frame_names]

            for i, file in enumerate(files):
                if file is None:
                    frame_names[i] = ''

            pcd_files = [file for file in files if file]
            frame_names = [frame_name for frame_name in frame_names if frame_name]

        seq_info.frame_names = frame_names
        point_clouds = (PyntCloud.from_file(str(pcd_file)).points.values for pcd_file in pcd_files)
        return seq_info, frame_names, pcd_files, point_clouds

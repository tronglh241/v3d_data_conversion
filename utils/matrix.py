from typing import Dict, Tuple

import numpy as np
import torch


def homo_mat(transform_matrix: np.ndarray) -> np.ndarray:
    padding = (4 - transform_matrix.shape[0], 4 - transform_matrix.shape[1])
    assert not any(map(lambda x: x < 0, padding)), padding

    if padding != (0, 0):
        transform_matrix = np.pad(transform_matrix, ((0, padding[0]), (0, padding[1])))
        transform_matrix[-1, -1] = 1.0

    assert transform_matrix.shape == (4, 4)
    return transform_matrix


def inv_mat(transform_matrix: np.ndarray, ret_homo: bool = False) -> np.ndarray:
    transform_matrix = homo_mat(transform_matrix)
    transform_matrix = np.linalg.inv(transform_matrix)

    if not ret_homo:
        transform_matrix = transform_matrix[:3]

    return transform_matrix


def point_3d_transfrom(points: np.ndarray, transform_matrix: np.ndarray, cuda: bool = False,
                       device: str = 'cuda') -> np.ndarray:
    points = np.hstack((points, np.ones((points.shape[0], 1))))
    assert len(points.shape) == 2 and points.shape[1] == 4
    assert all(points[:, 3] == 1.0)
    transform_matrix = homo_mat(transform_matrix)
    points = points.T

    if cuda:
        transform_matrix = torch.from_numpy(transform_matrix).to(device)  # type: ignore
        points = torch.from_numpy(points).to(device)  # type: ignore

    points = transform_matrix @ points

    if cuda:
        points = points.cpu().numpy()

    points = points.T
    points = points / points[:, 3:]
    points = points[:, :3]
    return points


def map_dimension(transform_matrix: np.ndarray, src_dim_map: Dict[str, float],
                  dst_dim_map: Dict[str, str]) -> Tuple[float, float, float]:
    '''
        Args:
            transform_matrix (np.ndarray): Transform matrix has shape of (3, 4).
            src_dim_map (dict):
                e.g. {
                    'x': 10.0,
                    'y': 5.0,
                    'z': 1.0,
                }
            dst_dim_map (dict):
                e.g. {
                    'width': 'x',
                    'height': 'y',
                    'length': 'z',
                }
        Returns: Tuple of (width, height, length) in the destination coordinate system.
    '''

    def find_coord_map(matrix: np.ndarray) -> Dict[str, str]:
        assert matrix.shape == (3, 4)
        axis_point_map = {
            'x': np.array([10, 0, 0]),
            'y': np.array([0, 10, 0]),
            'z': np.array([0, 0, 10]),
        }
        coord_map = {}

        for axis, point in axis_point_map.items():
            point = np.array([point])
            point = point_3d_transfrom(point, matrix)[0]
            idx = np.abs(point).argmax()
            coord_map[list(axis_point_map)[idx]] = axis

        return coord_map

    coord_map = find_coord_map(transform_matrix)
    width = src_dim_map[coord_map[dst_dim_map['width']]]
    height = src_dim_map[coord_map[dst_dim_map['height']]]
    length = src_dim_map[coord_map[dst_dim_map['length']]]

    return width, height, length

from __future__ import annotations

import abc
from typing import Any, Dict, List, Optional

from .base import Element


class Instance(Element):
    keywords: Optional[List[str]] = None

    @classmethod
    def parse(cls, instance: dict) -> Instance:
        pass

    @abc.abstractproperty
    def json(self) -> dict:
        pass

    @classmethod
    def is_compatitable(cls, instance: Any) -> bool:
        if cls.keywords is None:
            raise ValueError('Class `keywords` must be not None.')
        else:
            keywords = cls.keywords

        return (isinstance(instance, dict) and all(map(lambda keyword: keyword in keywords, instance)))


class Edge(Element):
    def __init__(self, type_: str, x1: float, y1: float, x2: float, y2: float, description: str):
        super(Edge, self).__init__()
        self.type = type_
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.description = description

    @classmethod
    def parse(cls, edge: dict) -> Edge:
        type_ = edge['type']
        x1 = edge['x1']
        y1 = edge['y1']
        x2 = edge['x2']
        y2 = edge['y2']
        description = edge['description']
        return cls(type_, x1, y1, x2, y2, description)

    @property
    def json(self) -> dict:
        edge = {
            'type': self.type,
            'x1': self.x1,
            'y1': self.y1,
            'x2': self.x2,
            'y2': self.y2,
            'description': self.description,
        }
        return edge


class Vertex(Element):
    def __init__(self, type_: str, x: float, y: float, description: str):
        super(Vertex, self).__init__()
        self.type = type_
        self.x = x
        self.y = y
        self.description = description

    @classmethod
    def parse(cls, vertex: dict) -> Vertex:
        type_ = vertex['type']
        x = vertex['x']
        y = vertex['y']
        description = vertex['description']
        return cls(type_, x, y, description)

    @property
    def json(self) -> dict:
        vertex = {
            'type': self.type,
            'x': self.x,
            'y': self.y,
            'description': self.description,
        }
        return vertex


class Coord2D(Element):
    def __init__(self, x: float, y: float):
        super(Coord2D, self).__init__()
        self.x = x
        self.y = y

    @classmethod
    def parse(cls, coord2d: Dict[str, float]) -> Coord2D:
        x = coord2d['x']
        y = coord2d['y']
        return cls(x, y)

    @property
    def json(self) -> Dict[str, float]:
        coord2d = {
            'x': self.x,
            'y': self.y,
        }
        return coord2d


class Coord3D(Element):
    def __init__(self, x: float, y: float, z: float):
        super(Coord3D, self).__init__()
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def parse(cls, coord3d: Dict[str, float]) -> Coord3D:
        x = coord3d['x']
        y = coord3d['y']
        z = coord3d['z']
        return cls(x, y, z)

    @property
    def json(self) -> Dict[str, float]:
        coord3d = {
            'x': self.x,
            'y': self.y,
            'z': self.z,
        }
        return coord3d


class Annotation(Element):
    def __init__(self, type_: str, label: str, edges: List[Edge], vertices: List[Vertex], points_2d: List[Coord2D],
                 points_3d: List[Coord3D], cuboid_uuid: str, not_in_lidar: bool, attributes: List[dict] = None):
        super(Annotation, self).__init__()
        self.type = type_
        self.attributes = attributes
        self.label = label
        self.edges = edges
        self.vertices = vertices
        self.points_2d = points_2d
        self.points_3d = points_3d
        self.cuboid_uuid = cuboid_uuid
        self.not_in_lidar = not_in_lidar

    @classmethod
    def parse(cls, annotation: dict) -> Annotation:
        type_ = annotation['type']
        attributes = annotation.get('attributes')
        label = annotation['label']
        edges = [Edge.parse(edge) for edge in annotation['edges']]
        vertices = [Vertex.parse(vertex) for vertex in annotation['vertices']]
        points_2d = [Coord2D.parse(coord) for coord in annotation['points_2d']]
        points_3d = [Coord3D.parse(coord) for coord in annotation['points_3d']]
        cuboid_uuid = annotation['cuboid_uuid']
        not_in_lidar = annotation['not_in_lidar']
        return cls(type_, label, edges, vertices, points_2d, points_3d, cuboid_uuid, not_in_lidar, attributes)

    @property
    def json(self) -> dict:
        annotation = {
            'type': self.type,
            'attributes': self.attributes,
            'label': self.label,
            'edges': [edge.json for edge in self.edges],
            'vertices': [vertex.json for vertex in self.vertices],
            'points_2d': [coord.json for coord in self.points_2d],
            'points_3d': [coord.json for coord in self.points_3d],
            'cuboid_uuid': self.cuboid_uuid,
            'not_in_lidar': self.not_in_lidar,
        }
        return annotation


class Instance2D(Instance):
    keywords = [
        'annotations',
        'camera_used',
    ]

    def __init__(self, annotations: List[Annotation], camera_used: int):
        super(Instance2D, self).__init__()
        self.annotations = annotations
        self.camera_used = camera_used

    @classmethod
    def parse(cls, instance: dict) -> Instance2D:
        annotations = [Annotation.parse(annotation) for annotation in instance['annotations']]
        camera_used = instance['camera_used']
        return cls(annotations, camera_used)

    @property
    def json(self) -> dict:
        instance = {
            'annotations': [annotation.json for annotation in self.annotations],
            'camera_used': self.camera_used,
        }
        return instance


class Instance3D(Instance):
    keywords = [
        'uuid',
        'label',
        'position',
        'dimensions',
        'yaw',
        'stationary',
        'camera_used',
        'numberOfPoints',
        'attributes',
    ]

    def __init__(self, uuid: str, label: str, position: Coord3D, dimensions: Coord3D, yaw: float, stationary: bool,
                 camera_used: int, numberOfPoints: int, attributes: dict = None):
        super(Instance3D, self).__init__()
        self.uuid = uuid
        self.label = label
        self.position = position
        self.dimensions = dimensions
        self.yaw = yaw
        self.stationary = stationary
        self.camera_used = camera_used
        self.numberOfPoints = numberOfPoints
        self.attributes = attributes

    @classmethod
    def parse(cls, instance: dict) -> Instance3D:
        uuid = instance['uuid']
        label = instance['label']
        position = Coord3D.parse(instance['position'])
        dimensions = Coord3D.parse(instance['dimensions'])
        yaw = instance['yaw']
        stationary = instance['stationary']
        camera_used = instance['camera_used']
        numberOfPoints = instance['numberOfPoints']
        attributes = instance.get('attributes')
        return cls(uuid, label, position, dimensions, yaw, stationary, camera_used, numberOfPoints, attributes)

    @property
    def json(self) -> dict:
        instance = {
            'uuid': self.uuid,
            'label': self.label,
            'position': self.position.json,
            'dimensions': self.dimensions.json,
            'yaw': self.yaw,
            'stationary': self.stationary,
            'camera_used': self.camera_used,
            'numberOfPoints': self.numberOfPoints,
        }

        if self.attributes is not None:
            instance['attributes'] = self.attributes

        return instance

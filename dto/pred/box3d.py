from abstract.dto import DTO


class LiDARBox3D(DTO):
    '''Each argument is defined as the definition in 3DBAT.'''

    def __init__(self, type_: str, x: float, y: float, z: float, x_size: float, y_size: float, z_size: float,
                 rotation_y: float, score: float = None, trackId: int = None):
        super(LiDARBox3D, self).__init__()
        self.type = type_
        self.x = x
        self.y = y
        self.z = z
        self.x_size = x_size
        self.y_size = y_size
        self.z_size = z_size
        self.rotation_y = rotation_y
        self.score = score
        self.trackId = trackId

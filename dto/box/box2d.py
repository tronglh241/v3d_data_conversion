from abstract.dto import DTO


class Box2D(DTO):
    def __init__(self, left: int, top: int, right: int, bottom: int, type_: str, track_id: int = None):
        super(Box2D, self).__init__()
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.type = type_
        self.track_id = track_id

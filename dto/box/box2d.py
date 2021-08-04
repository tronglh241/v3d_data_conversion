from abstract.dto import DTO


class Box2D(DTO):
    def __init__(self, left: int, top: int, right: int, bottom: int, type_: str):
        super(Box2D, self).__init__()
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.type = type_

from abstract.dto import DTO


class FrameInfo(DTO):
    def __init__(self, frame_name: str = None, pcd_file: str = None, image_file: str = None,
                 calib_file: str = None, label_file: str = None):
        super(FrameInfo, self).__init__()
        self.frame_name = frame_name
        self.pcd_file = pcd_file
        self.image_file = image_file
        self.calib_file = calib_file
        self.label_file = label_file

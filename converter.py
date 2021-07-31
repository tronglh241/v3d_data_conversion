from abstract.project import Project
from dto.seq.seq_info import SeqInfo
from utils.config import CfgNode


class Converter(Project):
    def __init__(self, config_path: str = None):
        super(Converter, self).__init__(config_path)
        config = CfgNode.load_yaml_with_base(str(self.config_path))
        self.stages, _ = config.eval()

    def run(self, seq_dir: str, out_dir: str) -> SeqInfo:
        seq_info = SeqInfo(seq_dir, out_dir)

        for stage in self.stages:
            seq_info, = self.stages[stage](seq_info)

        return seq_info

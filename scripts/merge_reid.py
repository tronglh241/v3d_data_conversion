import argparse
import shutil
from pathlib import Path

from tqdm import tqdm

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('out_dir')
    parser.add_argument('root_dir')

    parser.add_argument('--delivery-dir', '-d', nargs='*')
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    root_dir = Path(args.root_dir)

    instance_cnt = {}

    for delivery_dir in tqdm(args.delivery_dir):
        for split_dir in root_dir.joinpath(delivery_dir).glob('*'):
            out_split_dir = out_dir.joinpath(split_dir.name)
            if split_dir.name not in instance_cnt:
                instance_cnt[split_dir.name] = len(list(out_split_dir.glob('*')))

            for instance in split_dir.glob('*'):

                for dir_ in instance.glob('*'):
                    _out_split_dir = out_split_dir.joinpath(f'{instance_cnt[split_dir.name] + 1:04d}', dir_.name)
                    _out_split_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(str(dir_), str(_out_split_dir), dirs_exist_ok=True)

                instance_cnt[split_dir.name] += 1

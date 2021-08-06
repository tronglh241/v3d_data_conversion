import argparse
import shutil
from pathlib import Path

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('out_dir')
    parser.add_argument('root_dir')

    parser.add_argument('--delivery-dir', '-d', nargs='*')
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    root_dir = Path(args.root_dir)

    for delivery_dir in args.delivery_dir:
        for split_dir in root_dir.joinpath(delivery_dir).glob('*'):
            out_split_dir = out_dir.joinpath(split_dir.name)
            shutil.copytree(str(split_dir), str(out_split_dir), dirs_exist_ok=True)

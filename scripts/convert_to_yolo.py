import argparse
import os
import shutil
import sys
import traceback
from datetime import datetime
from pathlib import Path

from natsort import natsorted
from tqdm import tqdm

sys.path.append(os.getcwd())

from converter import Converter  # noqa: E402
from utils.common import open_file  # noqa: E402


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    parser.add_argument('out_dir')
    parser.add_argument('root_dir')

    parser.add_argument('--delivery-dir', '-d', nargs='*')
    parser.add_argument('--seq-dir', '-s', nargs='*')
    parser.add_argument('--seq-from', '-sf', type=int)
    parser.add_argument('--seq-to', '-st', type=int)

    parser.add_argument('--train-ratio', type=float, default=0.8)
    parser.add_argument('--val-ratio-in-train', type=float, default=0.2)

    args = parser.parse_args()

    # Check args
    if (args.seq_from is None) != (args.seq_to is None):
        raise argparse.ArgumentError(None, 'Both --seq-from and --seq-to are specified.')

    return args


def glob_seq_dirs(args):
    # Glob seq_dirs
    root_dir = Path(args.root_dir)
    delivery_dirs = ([root_dir.joinpath(delivery_dir) for delivery_dir in args.delivery_dir]
                     if args.delivery_dir else [root_dir])

    for delivery_dir in delivery_dirs:
        if not delivery_dir.is_dir():
            print(f'{delivery_dir} is not a folder.')

    delivery_dirs = list(filter(lambda delivery_dir: delivery_dir.is_dir(), delivery_dirs))

    if args.seq_dir:
        seq_dirs = [delivery_dir.joinpath(seq_dir) for delivery_dir in delivery_dirs
                    for seq_dir in args.seq_dir]
    elif args.seq_from is not None and args.seq_to is not None:
        seq_dirs = [delivery_dir.joinpath(str(i)) for delivery_dir in delivery_dirs
                    for i in range(args.seq_from, args.seq_to + 1)]
    else:
        seq_dirs = [seq_dir for delivery_dir in delivery_dirs
                    for seq_dir in natsorted(delivery_dir.glob('*'))]

    for seq_dir in seq_dirs:
        if not seq_dir.is_dir():
            print(f'{seq_dir} is not a folder.')

    seq_dirs = list(filter(lambda seq_dir: seq_dir.is_dir(), seq_dirs))
    return seq_dirs


if __name__ == '__main__':
    args = parse_args()
    seq_dirs = glob_seq_dirs(args)

    # Convert data
    out_dir = Path(args.out_dir)

    if len(list(out_dir.glob('*'))):
        raise RuntimeError('out_dir is not empty.')

    converter = Converter(args.config)

    for seq_dir in tqdm(seq_dirs):
        try:
            converter(str(seq_dir), args.out_dir)
        except Exception as e:
            with open_file('log.txt', mode='a', encoding='utf-8') as f:
                f.write(f'{datetime.now()}: Error while converting {seq_dir}, {e}\n')
                f.write(f'{traceback.format_exc()}\n')

    instances = [dir_ for dir_ in out_dir.glob('*')]
    train_split = instances[:round(len(instances) * args.train_ratio)]
    test_split = instances[round(len(instances) * args.train_ratio):]
    val_split = train_split[round(len(train_split) * (1.0 - args.val_ratio_in_train)):]
    train_split = train_split[:round(len(train_split) * (1.0 - args.val_ratio_in_train))]

    split_map = {
        'train': train_split,
        'val': val_split,
        'test': test_split,
    }

    for split_name, split in split_map.items():
        image_dir = out_dir.joinpath(split_name, 'images')
        label_dir = out_dir.joinpath(split_name, 'labels')
        image_dir.mkdir(parents=True, exist_ok=True)
        label_dir.mkdir(parents=True, exist_ok=True)

        for instance in split:
            for image in instance.joinpath('images').glob('*.*'):
                shutil.move(str(image), image_dir)
            for label in instance.joinpath('labels').glob('*.*'):
                shutil.move(str(label), label_dir)

    for dir_ in instances:
        shutil.rmtree(str(dir_))

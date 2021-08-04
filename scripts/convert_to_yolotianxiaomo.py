import argparse
import os
import sys
import traceback
from pathlib import Path

from natsort import natsorted
from tqdm import tqdm

sys.path.append(os.getcwd())

from converter import Converter  # noqa: E402
from modules.label.label_to_yolotianxiaomo.processor import \
    LABEL_FILENAME  # noqa: E402
from utils.common import open_file  # noqa: E402


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('out_dir')
    parser.add_argument('root_dir')

    parser.add_argument('--config', default='configs/bat3d_to_yolotianxiaomo.yaml')
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
    converter = Converter(args.config)

    if len(list(out_dir.glob('*'))):
        raise RuntimeError('out_dir is not empty.')

    for seq_dir in tqdm(seq_dirs):
        try:
            converter(str(seq_dir), args.out_dir)
        except Exception as e:
            print(f'Error while converting {seq_dir}', e)
            traceback.print_exc()

    label_file = out_dir.joinpath(LABEL_FILENAME)
    with label_file.open(mode='r', encoding='utf-8') as f:
        frames = list(f)

    train_split = frames[:round(len(frames) * args.train_ratio)]
    test_split = frames[round(len(frames) * args.train_ratio):]
    val_split = train_split[round(len(train_split) * (1.0 - args.val_ratio_in_train)):]
    train_split = train_split[:round(len(train_split) * (1.0 - args.val_ratio_in_train))]

    split_map = {
        'train': train_split,
        'val': val_split,
        'test': test_split,
    }

    for split_name, split in split_map.items():
        with open_file(str(out_dir.joinpath(f'{split_name}.txt')), mode='w', encoding='utf-8') as f:
            for lines in split:
                f.writelines(lines)

    label_file.unlink()

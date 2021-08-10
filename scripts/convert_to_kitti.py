import argparse
import os
import shutil
import sys
import traceback
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from natsort import natsorted
from tqdm import tqdm

sys.path.append(os.getcwd())

from converter import Converter  # noqa: E402
from utils.common import open_file  # noqa: E402

kitti_dirs = ['ImageSets', 'training', 'testing']
cnt: Dict[str, int] = defaultdict(int)


def get_all_frames(seq_dirs: List[Path], data_dirs: Dict[str, str]) -> List[Dict[str, Path]]:
    frames = []
    for seq_dir in seq_dirs:
        frames_in_seq: Dict[str, Dict[str, Path]] = defaultdict(dict)

        for data_dir, file_suffix in data_dirs.items():
            for data_file in natsorted(seq_dir.joinpath(data_dir).glob(f'*{file_suffix}')):
                frames_in_seq[data_file.stem][data_dir] = data_file

        for frame_name, frame_data in frames_in_seq.items():
            if all([data_dir in frame_data for data_dir in data_dirs]):
                frames.append(frame_data)

    return frames


def mv_data(frames: List[Dict[str, Path]], out_dir: str, train_ratio: float,
            data_dirs: Dict[str, str]) -> Dict[str, List[str]]:
    frame_names = defaultdict(list)
    out_dir = Path(out_dir)

    train_split = frames[:round(train_ratio * len(frames))]
    test_split = frames[round(train_ratio * len(frames)):]
    mapping = {
        'training': train_split,
        'testing': test_split,
    }

    for split_name, split_part in mapping.items():
        split_dir = out_dir.joinpath(split_name)

        # Create folders
        for data_dirname in data_dirs:
            data_dir = split_dir.joinpath(data_dirname)
            data_dir.mkdir(parents=True, exist_ok=True)

        # Copy frame files to target folders
        for frame in split_part:
            frame_name = f'{cnt[split_name]:06d}'

            for data_dirname, data_file in frame.items():
                src = data_file
                dst = split_dir.joinpath(data_dirname, frame_name).with_suffix(data_file.suffix)
                shutil.move(str(src), str(dst))

            cnt[split_name] += 1
            frame_names[split_name].append(frame_name)

    return frame_names


def rm_seq_dirs(seq_dirs: List[Path]) -> None:
    for seq_dir in seq_dirs:
        shutil.rmtree(str(seq_dir))


def mk_image_sets(frame_names: Dict[str, List[str]], out_dir: str, valid_ratio_in_train: float) -> None:
    mapping = {
        'train': frame_names['training'],
        'test': frame_names['testing'],
    }

    mapping['val'] = mapping['train'][round((1.0 - valid_ratio_in_train) * len(mapping['train'])):]
    mapping['train'] = mapping['train'][:round((1.0 - valid_ratio_in_train) * len(mapping['train']))]

    image_sets_dir = Path(out_dir).joinpath('ImageSets')

    if not image_sets_dir.exists():
        image_sets_dir.mkdir(parents=True)

    for split_name, names in mapping.items():
        with image_sets_dir.joinpath(f'{split_name}.txt').open(mode='w', encoding='utf-8') as f:
            names = [f'{name}\n' for name in names]
            f.writelines(names)


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
    parser.add_argument('--not-organize-dir', '-no', action='store_true')
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
    data_dirs = converter.stages.pop('data_dirs', None)

    for seq_dir in tqdm(seq_dirs):
        try:
            converter(str(seq_dir), args.out_dir)
        except Exception as e:
            with open_file('log.txt', mode='a', encoding='utf-8') as f:
                f.write(f'{datetime.now()}: Error while converting {seq_dir}, {e}\n')
                f.write(f'{traceback.format_exc()}\n')

    seq_dirs = [seq_dir for seq_dir in natsorted(out_dir.glob('*'))
                if seq_dir.is_dir() and seq_dir.stem not in kitti_dirs]

    if not args.not_organize_dir and seq_dirs and data_dirs:
        frames = get_all_frames(seq_dirs, data_dirs)
        frame_names = mv_data(frames, str(out_dir), args.train_ratio, data_dirs)
        rm_seq_dirs(seq_dirs)
        mk_image_sets(frame_names, str(out_dir), args.val_ratio_in_train)

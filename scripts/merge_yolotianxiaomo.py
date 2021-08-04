import argparse
from pathlib import Path

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('out_dir')
    parser.add_argument('root_dir')
    parser.add_argument('--delivery-dir', '-d', nargs='*')
    args = parser.parse_args()

    splits = [
        'train',
        'val',
        'test',
    ]

    out_dir = Path(args.out_dir)
    root_dir = Path(args.root_dir)
    delivery_dirs = ([root_dir.joinpath(delivery_dir) for delivery_dir in args.delivery_dir]
                     if args.delivery_dir else [root_dir])

    for delivery_dir in delivery_dirs:
        if not delivery_dir.is_dir():
            print(f'{delivery_dir} is not a folder.')

    delivery_dirs = list(filter(lambda delivery_dir: delivery_dir.is_dir(), delivery_dirs))

    out_dir.mkdir(parents=True, exist_ok=True)
    for split in splits:
        label_file = out_dir.joinpath(f'{split}.txt')
        with label_file.open(mode='a', encoding='utf-8') as fw:
            for delivery_dir in delivery_dirs:
                with delivery_dir.joinpath(f'{split}.txt').open(mode='r', encoding='utf-8') as fr:
                    fw.writelines(fr)

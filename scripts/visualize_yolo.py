import argparse
from pathlib import Path

import cv2
from tqdm import tqdm

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('out_dir')
    parser.add_argument('data_dir')
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    data_dir = Path(args.data_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    class_mapping = {
        'Motorbike': 0,
        'Car': 1,
        'Pedestrian': 2,
    }
    class_mapping = {v: k for k, v in class_mapping.items()}

    for label_file in tqdm(list(data_dir.glob('**/*.txt'))):
        image_file = str(Path(str(label_file).replace('labels', 'images')).with_suffix('.jpg'))
        image = cv2.imread(image_file)

        with open(str(label_file)) as f:
            for line in f:
                class_id, cx, cy, w, h = list(map(lambda x: float(x), line.strip().split()))
                class_ = class_mapping[int(class_id)]
                left = round((cx - w / 2) * image.shape[1])
                right = round((cx + w / 2) * image.shape[1])
                top = round((cy - h / 2) * image.shape[0])
                bottom = round((cy + h / 2) * image.shape[0])
                image = cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), thickness=2)
                image = cv2.putText(image, class_, (left, bottom), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255))

        cv2.imwrite(str(out_dir.joinpath(Path(image_file).name)), image)

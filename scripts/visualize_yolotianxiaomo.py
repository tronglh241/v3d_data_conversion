import argparse
from pathlib import Path

import cv2

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('label_file')
    parser.add_argument('out_dir')
    args = parser.parse_args()

    class_id = {
        'Motorbike': 0,
        'Car': 1,
        'Pedestrian': 2,
    }

    class_id = {v: k for k, v in class_id.items()}

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.label_file, mode='r', encoding='utf-8') as f:
        for line in f:
            image_file, *boxes = line.strip().split()
            boxes = list(map(lambda x: int(x), boxes))
            boxes = [boxes[i:i + 5] for i in range(0, len(boxes), 5)]

            image = cv2.imread(image_file)
            image_file = out_dir.joinpath(*Path(image_file).parts[-4:])
            image_file.parent.mkdir(parents=True, exist_ok=True)

            for box in boxes:
                image = cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), thickness=2)
                image = cv2.putText(image, class_id[box[4]], (box[0], box[3]), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255))
                cv2.imwrite(str(image_file), image)

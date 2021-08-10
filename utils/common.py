from pathlib import Path
from typing import Any, Optional, TextIO


def abs_path(path):
    if Path(path).is_absolute():
        return path
    else:
        return str(Path(__file__).parents[1].joinpath(path))


def open_file(file_path: str, *args: Any, **kwargs: Any) -> TextIO:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path.open(*args, **kwargs)


def get_file_with_stem(dirname: str, stem: str, suffix: str = '.*', abs_path: bool = True) -> Optional[str]:
    files = list(Path(dirname).glob(f'{stem}{suffix}'))

    if len(files) == 0:
        return None
    elif len(files) == 1:
        if abs_path:
            return str(files[0].resolve())
        else:
            return str(files[0])
    else:
        raise RuntimeError(f'There are more than one file having stem {stem} in {dirname}.')

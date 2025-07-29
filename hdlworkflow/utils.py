from importlib.metadata import version
import logging
import os
import sys
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)


def is_file(file: str) -> bool:
    filepath = Path(file)
    return filepath.is_file()


def prepend_pwd_if_relative(paths: List[str], pwd: str) -> List[str]:
    result: List[str] = []
    for path in paths:
        if os.path.isabs(path):
            result.append(path)
        else:
            result.append(pwd + "/" + path)
    return result


def get_cocotb_version() -> Tuple[int, int, int]:
    return __get_semantic_version(version("cocotb"))


def __get_semantic_version(ver: str) -> Tuple[int, int, int]:
    v = ver.split(".")
    if len(v) < 3:
        logger.error(f"Expecting MAJOR.MINOR.PATCH. Got: {'.'.join(str(num) for num in v)}")
        sys.exit(2)
    return tuple([int(num) for num in v[0:3]])

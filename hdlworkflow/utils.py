from importlib.metadata import version
import logging
import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ElementTree

logger = logging.getLogger(__name__)


def is_file(file: str) -> bool:
    filepath = Path(file)
    return filepath.is_file()


def prepend_pwd_if_relative(paths: list[str], pwd: str) -> list[str]:
    result: list[str] = []
    for path in paths:
        if os.path.isabs(path):
            result.append(path)
        else:
            result.append(pwd + "/" + path)
    return result


def get_cocotb_version() -> tuple[int, int, int]:
    return __get_semantic_version(version("cocotb"))


def __get_semantic_version(ver: str) -> tuple[int, int, int]:
    v = ver.split(".")
    if len(v) < 3:
        logger.error(f"Expecting MAJOR.MINOR.PATCH. Got: {'.'.join(str(num) for num in v)}")
        sys.exit(2)
    return tuple([int(num) for num in v[0:3]])


def is_cocotb_test_pass(xml_file: str) -> bool:
    logger.info("Checking cocotb pass or fail...")
    tree = ElementTree.parse(xml_file)
    root = tree.getroot()
    num_failures = 0
    for failure in root.iter("failure"):
        num_failures += 1

    return num_failures == 0

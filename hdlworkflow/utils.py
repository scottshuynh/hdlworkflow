import logging
import os
import re
import sys
from importlib.metadata import version
from pathlib import Path
import xml.etree.ElementTree as ElementTree

logger = logging.getLogger(__name__)


def relative_to_absolute_paths(paths: list[str], pwd: str | Path) -> list[str]:
    result: list[str] = []
    for path in paths:
        if Path(path).is_absolute():
            result.append(path)
        else:
            result.append(str(Path(Path(pwd) / path).resolve(False)))
    return result


_ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def sanitise_filename(filename: str) -> str:
    """Remove illegal characters in filename"""
    return _ILLEGAL.sub("", filename)


def truncate_filestem(filestem: str, suffix: str, max_bytes: int = 255) -> str:
    """Truncates the file stem if the filename exceeds 255 bytes.
    Returns the truncated filename
    """
    budget = max_bytes - len(suffix.encode("utf-8"))
    stem = filestem.encode("utf-8")[:budget].decode("utf-8", errors="ignore")
    return stem + suffix


def get_cocotb_version() -> tuple[int, int, int]:
    return _get_semantic_version(version("cocotb"))


def _get_semantic_version(ver: str) -> tuple[int, int, int]:
    v = ver.split(".")
    if len(v) < 3:
        logger.error(f"Expecting MAJOR.MINOR.PATCH. Got: {'.'.join(str(num) for num in v)}")
        sys.exit(2)
    return tuple([int(num) for num in v[0:3]])


def is_cocotb_test_pass(xml_file: str) -> bool:
    if os.path.isfile(xml_file):
        logger.info("Checking cocotb pass or fail...")
        tree = ElementTree.parse(xml_file)
        root = tree.getroot()
        num_failures = 0
        for _ in root.iter("failure"):
            num_failures += 1

        return num_failures == 0
    else:
        logger.error(f"Unable to find {xml_file}. Cocotb test incomplete.")
        return False

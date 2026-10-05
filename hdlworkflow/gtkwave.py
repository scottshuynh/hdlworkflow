import logging
import subprocess
import sys
from pathlib import Path
from shutil import which

logger = logging.getLogger(__name__)


class Gtkwave:
    """View waveforms using gtkwave."""

    def __init__(self, waveform_dump_file: Path, waveform_save_file: Path):
        logger.info(f"Initialising {type(self).__name__}...")
        self._waveform_dump_file = waveform_dump_file
        self._waveform_save_file = waveform_save_file

        if waveform_dump_file:
            if waveform_dump_file.suffix != ".fst":
                logger.error(f"Expecting waveform dump file with .fst extension. Got file: {waveform_dump_file}")
                sys.exit(1)
        else:
            logger.error("Waveform dump file must be specified.")
            sys.exit(1)

        if waveform_save_file:
            if waveform_save_file.suffix != ".gtkw":
                logger.error(f"Expecting waveform view file with .gtkw extension. Got: {waveform_save_file}")
                sys.exit(1)
        else:
            logger.error("Waveform save file must be specified.")
            sys.exit(1)

        if not self._check_dependency():
            logger.error("Missing dependency: gtkwave")
            logger.error("All dependencies must be found on PATH.")
            sys.exit(1)

    def _check_dependency(self) -> bool:
        logger.info("Checking dependencies...")
        if not which("gtkwave"):
            return False
        return True

    def run(self):
        logger.info("Running gtkwave...")
        command = ["gtkwave", str(self._waveform_dump_file), "-a", str(self._waveform_save_file)]
        logger.info("    " + " ".join(cmd for cmd in command))
        gtkwave = subprocess.run(command)
        if gtkwave.returncode != 0:
            logger.error("Error while running gtkwave.")
            sys.exit(1)

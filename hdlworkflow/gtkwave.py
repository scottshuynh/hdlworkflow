import logging
import subprocess
import sys
from shutil import which

logger = logging.getLogger(__name__)


class Gtkwave:
    """View waveforms using gtkwave."""

    def __init__(self, waveform_data: str, waveform_save_file: str):
        logger.info(f"Initialising {type(self).__name__}...")
        self.__waveform_data = waveform_data

        if waveform_save_file:
            self.__waveform_save = waveform_save_file
        else:
            logger.error("Waveform save file must be specified.")
            sys.exit(1)

        if not self.__check_dependency():
            logger.error("Missing dependency: gtkwave")
            logger.error("All dependencies must be found on PATH.")
            sys.exit(1)

    def __check_dependency(self) -> bool:
        logger.info("Checking dependencies...")
        if not which("gtkwave"):
            return False
        return True

    def run(self):
        logger.info("Running gtkwave...")
        command = ["gtkwave", self.__waveform_data, "-a", self.__waveform_save]
        logger.info("    " + " ".join(cmd for cmd in command))
        gtkwave = subprocess.run(command)
        if gtkwave.returncode != 0:
            logger.error("Error while running gtkwave.")
            sys.exit(1)

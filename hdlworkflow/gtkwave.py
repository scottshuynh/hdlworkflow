import logging
import subprocess
import sys
from shutil import which

logger = logging.getLogger(__name__)


class Gtkwave:
    """View waveforms using gtkwave."""

    def __init__(self, waveform_file: str):
        logger.info(f"Initialising {type(self).__name__}...")
        self.__waveform_file = waveform_file
        self.__waveform_save = self.__get_waveform_save_file()
        if not self.__check_dependency():
            logger.error("Missing dependency: gtkwave")
            logger.error("All dependencies must be found on PATH.")
            sys.exit(1)

    def __get_waveform_save_file(self):
        return self.__waveform_file.split(".")[0] + ".gtkw"

    def __check_dependency(self) -> bool:
        logger.info("Checking dependencies...")
        if not which("gtkwave"):
            return False
        return True

    def run(self):
        logger.info("Running gtkwave...")
        gtkwave = subprocess.run(["gtkwave", self.__waveform_file, "-a", self.__waveform_save])
        if gtkwave.returncode != 0:
            logger.error("Error while running gtkwave.")
            sys.exit(1)

import logging
import subprocess
import sys
from pathlib import Path
from shutil import which

logger = logging.getLogger(__name__)


class Surfer:
    """View waveforms using surfer."""

    def __init__(self, top: str, waveform_dump_file: Path, waveform_state_file: Path, overwrite_save_file: bool):
        logger.info(f"Initialising {type(self).__name__}...")
        self._top = top
        self._waveform_dump_file = waveform_dump_file
        self._waveform_state_file = waveform_state_file
        self._overwrite_save_file = overwrite_save_file

        if waveform_dump_file:
            if waveform_dump_file.suffix != ".fst":
                logger.error(f"Expecting waveform dump file with .fst extension. Got file: {waveform_dump_file}")
                sys.exit(1)
        else:
            logger.error("Waveform dump file must be specified.")
            sys.exit(1)

        if waveform_state_file:
            if waveform_state_file.suffix != ".ron":
                logger.error(f"Expecting waveform state file with .ron extension. Got file: {waveform_state_file}")
                sys.exit(1)
        else:
            logger.error("Waveform save file must be specified.")
            sys.exit(1)

        if not self._check_dependency():
            logger.error("Missing dependency: surfer")
            logger.error("All dependencies must be found on PATH.")
            sys.exit(1)

    def _check_dependency(self) -> bool:
        logger.info("Checking dependencies...")
        if not which("surfer"):
            return False
        return True

    def _generate_command_file(self) -> None:
        with open("commands.txt", "w", encoding="utf=8") as f:
            f.write(f"scope_add_as_group_recursive {self._top}\n")
            f.write(f"save_state_as {self._waveform_state_file}\n")

    def run(self):
        logger.info("Running surfer...")
        command = ["surfer", str(self._waveform_dump_file)]
        if self._overwrite_save_file:
            Path(self._waveform_state_file).unlink(missing_ok=True)
            self._generate_command_file()
            command.extend(["-c", "commands.txt"])
        else:
            command.extend(["-s", str(self._waveform_state_file)])

        logger.info("    " + " ".join(cmd for cmd in command))
        surfer = subprocess.run(command)
        if surfer.returncode != 0:
            logger.error("Error while running surfer.")
            sys.exit(1)

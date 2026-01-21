import logging, subprocess, sys
from pathlib import Path
from shutil import which

logger = logging.getLogger(__name__)


class Surfer:
    """View waveforms using surfer."""

    def __init__(self, top: str, waveform_data: str, waveform_save_file: str, overwrite_save_file: bool):
        logger.info(f"Initialising {type(self).__name__}...")
        self._top = top
        self._waveform_data = waveform_data
        self._overwrite_save_file = overwrite_save_file

        if waveform_save_file:
            self._waveform_save = waveform_save_file
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
            f.write(f"save_state_as {self._top}.ron\n")

    def run(self):
        logger.info("Running surfer...")
        command = ["surfer", self._waveform_data]
        if self._overwrite_save_file:
            Path(self._waveform_save).unlink(missing_ok=True)
            self._generate_command_file()
            command.extend(["-c", "commands.txt"])
        else:
            command.extend(["-s", self._waveform_save])

        logger.info("    " + " ".join(cmd for cmd in command))
        surfer = subprocess.run(command)
        if surfer.returncode != 0:
            logger.error("Error while running surfer.")
            sys.exit(1)

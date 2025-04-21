import subprocess
from shutil import which


class Gtkwave:
    """View waveforms using gtkwave."""

    def __init__(self, waveform_file: str):
        self.__waveform_file = waveform_file
        self.__waveform_save = self.__get_waveform_save_file()
        assert self.__check_dependency(), "Missing dependency: gtkwave"

    def __get_waveform_save_file(self):
        return self.__waveform_file.split(".")[0] + ".gtkw"

    def __check_dependency(self) -> bool:
        if not which("gtkwave"):
            return False
        return True

    def run(self):
        gtkwave = subprocess.run(["gtkwave", self.__waveform_file, "-a", self.__waveform_save])
        assert gtkwave.returncode == 0, "Error during run."

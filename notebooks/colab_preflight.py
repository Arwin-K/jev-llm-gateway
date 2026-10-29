"""Run in Colab before installing GPU packages; output contains no credentials."""

import json
import platform
import shutil
import subprocess
import sys


def version(command):
    if not shutil.which(command[0]):
        return "unavailable"
    result = subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)
    return (result.stdout or result.stderr).strip()[:2000]


if __name__ == "__main__":
    print(json.dumps({
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "nvidia_smi": version(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"]),
        "nvcc": version(["nvcc", "--version"]),
    }, indent=2))

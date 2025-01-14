#!/usr/bin/env python
from __future__ import annotations

import os
import subprocess
import sys
from functools import partial
from pathlib import Path

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    common_args = [
        "uv",
        "pip",
        "compile",
        "--quiet",
        "--generate-hashes",
        "--constraint",
        "-",
        "requirements.in",
        *sys.argv[1:],
    ]
    run = partial(subprocess.run, check=True)
    versions = ["3.10", "3.11", "3.12", "3.13"]
    django_versions = [(5,1)]
    for version in versions:
        for django_version in django_versions:
            version_val = f"{django_version[0]}.{django_version[1]}"
            version_val = float(version_val)
            input_str = f"Django>={version_val}a1,<{version_val+0.1}"
            input_str = input_str.encode("utf-8")
            run(
                [
                    *common_args,
                    "--python",
                    version,
                    "--output-file",
                    f"py{version.replace('.', '')}-django{django_version[0]}{django_version[1]}.txt",
                ],
                input=input_str,
            )


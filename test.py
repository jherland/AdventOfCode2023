#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

py_files = {p.stem: p for p in Path.cwd().glob("??.py")}
expect_files = {p.stem: p for p in Path.cwd().glob("??.expect")}
for stem in sorted(py_files.keys() | expect_files.keys()):
    print(f"--- {stem} ---")
    script = py_files[stem]
    expect = expect_files[stem].read_text()
    proc = subprocess.run(
        [sys.executable, script],  # noqa: S603
        capture_output=True,
        text=True,
        check=True,
    )
    if proc.stdout == expect:
        print(proc.stdout, end="")
    else:
        print(f"*** Test failed for day #{stem}!")
        print(f"    EXPECTED: {expect!r}")
        print(f"     BUT GOT: {proc.stdout!r}")
        sys.exit(1)

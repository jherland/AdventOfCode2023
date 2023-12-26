#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

py_files = {p.stem: p for p in Path.cwd().glob("??.py")}
expect_files = {p.stem: p for p in Path.cwd().glob("??.expect")}


def test(stem: str) -> int:
    print(f"--- Test day #{stem} ---")
    try:
        script = py_files[stem]
    except KeyError:
        print(f"Missing Python file for day #{stem}!")
        return 2
    try:
        expect = expect_files[stem].read_text()
    except KeyError:
        print(f"Missing expected output for day #{stem}!")
        return 3

    proc = subprocess.run(
        [sys.executable, script],  # noqa: S603
        capture_output=True,
        text=True,
        check=True,
    )
    if proc.stdout != expect:
        print(f"*** Test failed for day #{stem}!")
        print(f"    EXPECTED: {expect!r}")
        print(f"     BUT GOT: {proc.stdout!r}")
        return 1
    print(proc.stdout, end="")
    return 0


if len(sys.argv) >= 2:
    stems = sys.argv[1:]
else:
    stems = sorted(py_files.keys() | expect_files.keys())

for stem in stems:
    if retval := test(stem):
        sys.exit(retval)

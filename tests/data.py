#!/usr/bin/python3

""""Utilities for loading binary test data"""

from __future__ import annotations
from typing import Final
from pathlib import Path


BASE_PATH: Final = Path("tests/data/")


def load_test_data(path: str) -> memoryview:
    """Load a binary file containing test data"""
    with open(Path.cwd() / BASE_PATH / Path(path), "rb") as fd:
        return memoryview(fd.read())

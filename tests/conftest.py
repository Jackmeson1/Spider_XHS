import json
import os
from pathlib import Path

import pytest


def fake_resp(file_name: str) -> dict:
    base = Path(__file__).resolve().parent / "static"
    with open(base / file_name, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def patch_env(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COOKIES", "a=1;b=2")
    yield

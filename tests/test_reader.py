"""Smoke tests for DektakLoad against a real .OPDx fixture."""

import io
import logging
import pathlib
import struct
import subprocess
import sys

import numpy as np
import pytest

from OPDx_read.reader import DektakLoad

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "test1.OPDx"


def test_fixture_present():
    assert FIXTURE.is_file(), f"Test fixture missing at {FIXTURE}"


@pytest.fixture(scope="module")
def loader():
    return DektakLoad(str(FIXTURE))


def test_load_produces_items(loader):
    assert loader.items
    names = [i.name for i in loader.items if i is not None]
    assert "1D_Data" in names
    assert "MetaData" in names


def test_get_data_1d_returns_finite_arrays(loader):
    x, y = loader.get_data_1D()
    assert x is not None and y is not None
    assert x.shape == y.shape
    assert x.size > 0
    assert np.all(np.isfinite(y))


def test_get_data_2d_does_not_require_matplotlib(loader):
    """plot=False must not pull matplotlib in (regression test for the
    lazy-import refactor)."""
    result = loader.get_data_2D(plot=False)
    assert isinstance(result, tuple) and len(result) == 3


def test_get_metadata_returns_dict(loader):
    md = loader.get_metadata()
    assert isinstance(md, dict) and md
    assert "DataKind" in md or "DataSetName" in md


def test_module_import_does_not_eagerly_load_matplotlib():
    """`from OPDx_read.reader import DektakLoad` must work without matplotlib
    installed — guarantees the lazy import in get_data_2D stays lazy."""
    code = (
        "import sys; "
        "from OPDx_read.reader import DektakLoad; "
        "print('matplotlib' in sys.modules)"
    )
    out = subprocess.check_output([sys.executable, "-c", code], text=True)
    assert out.strip() == "False"


def test_read_name_falls_back_to_latin1_on_invalid_utf8():
    """Some legacy .OPDx files carry latin-1 bytes in name fields; read_name
    must not raise UnicodeDecodeError."""
    payload = struct.pack('i', 4) + b'\xe9\xe8\xe7\xe6'
    buf = io.BytesIO(payload)
    # read_name doesn't depend on instance state, so skip __init__ to avoid
    # opening a real file.
    loader = object.__new__(DektakLoad)
    assert loader.read_name(buf) == '\xe9\xe8\xe7\xe6'


def test_logger_silent_for_clean_fixture(caplog):
    """A well-formed .OPDx must not emit any WARNING/ERROR records from the
    parser. If this fires, either the fixture is unusual or the parser is
    triggering a spurious warning that needs investigating."""
    with caplog.at_level(logging.WARNING, logger="OPDx_read.reader"):
        DektakLoad(str(FIXTURE))
    bad = [r for r in caplog.records if r.name.startswith("OPDx_read")]
    assert not bad, f"unexpected logs: {[(r.levelname, r.message) for r in bad]}"

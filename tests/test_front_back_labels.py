"""Check the 2026-11-13 front/back convention fix.

'front' must mean curved first and 'back' flat first. The fix is a pure
relabel: the new 'front' reproduces the pre-fix 'back' exactly and vice versa.
The pre-fix module is read from git (commit 795e325); that part is skipped
when git or the commit is unavailable.

Run: python -m pytest tests/test_front_back_labels.py
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import optical_demo_utils as new  # noqa: E402

LEGACY_COMMIT = "795e325"
um = 1e-6


def _legacy_module(tmp_path):
    try:
        src = subprocess.run(
            ["git", "-C", str(ROOT), "show", f"{LEGACY_COMMIT}:optical_demo_utils.py"],
            check=True, capture_output=True, text=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("pre-fix module not available from git")
    path = tmp_path / "legacy_optical_demo_utils.py"
    path.write_text(src)
    spec = importlib.util.spec_from_file_location("legacy_optical_demo_utils", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _setup(n=192, px=1.0 * um, dia=160 * um, roc=300 * um, thick=20 * um, angle_deg=10.0):
    XX, YY, FX, FY = new.get_grids(n, n, px, "cpu")
    RR = torch.sqrt(XX**2 + YY**2)
    field = (RR <= 0.35 * dia).float()[None, None].to(torch.complex64)
    sag = roc - torch.sqrt(torch.clamp(roc**2 - RR**2, min=0.0))
    h_map = (thick - sag) * (RR <= 0.5 * dia).float()
    h_map = h_map - h_map.min()
    angle = {"x_rad": float(np.deg2rad(angle_deg)), "y_rad": float(np.deg2rad(0.5 * angle_deg))}
    return dict(XX=XX, YY=YY, FX=FX, FY=FY, field=field, h_map=h_map, px=px, angle=angle,
                k0=2 * np.pi / (0.55 * um))


def _run(mod, g, method, direction):
    lpc = {} if "LPC" in method else None
    if method.startswith("MS"):
        return mod.ms_as_engine(g["field"], g["h_map"], 5 * um, g["k0"], 1.54, 1.0, g["FX"], g["FY"],
                                g["XX"], g["YY"], g["px"], heightmapDirection=direction,
                                lpc_params=lpc, angle_params=g["angle"])
    return mod.ss_as_engine(g["field"], g["h_map"], g["k0"], 1.54, 1.0, g["FX"], g["FY"],
                            g["XX"], g["YY"], g["px"], heightmapDirection=direction,
                            lpc_params=lpc, angle_params=g["angle"])


@pytest.mark.parametrize("method", ["MS", "MS+LPC", "SS", "SS+LPC"])
def test_new_labels_are_swapped_legacy_labels(tmp_path, method):
    legacy = _legacy_module(tmp_path)
    g = _setup()
    for new_dir, old_dir in (("front", "back"), ("back", "front")):
        a = _run(new, g, method, new_dir)
        b = _run(legacy, g, method, old_dir)
        rel = (torch.linalg.vector_norm(a - b) / torch.linalg.vector_norm(b)).item()
        assert rel < 1e-6, (method, new_dir, rel)


def test_front_starts_at_apex_slice():
    g = _setup()
    dz = 5 * um
    first_front, _ = new.heightmap_slicer(g["h_map"], dz, 0, "front")
    first_back, _ = new.heightmap_slicer(g["h_map"], dz, 0, "back")
    # The apex slice has the smallest footprint, the base slice the largest.
    assert (first_front > 0).sum() < (first_back > 0).sum()


def test_unknown_direction_is_rejected():
    with pytest.raises(ValueError):
        new.is_curved_first("curved")

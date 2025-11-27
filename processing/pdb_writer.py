"""Utilities for writing enhanced PDB files."""

from __future__ import annotations

import math
from io import StringIO
from typing import Dict


def generate_enhanced_pdb(
    weights: Dict[str, float],
    source_mer: str,
    original_file: str,
    _mers,
) -> str:
    """
    Copy every original atom line. Put distance/weight for the atom’s Mer
    into the B-factor (TempFactor) column. Adds one REMARK before coords.
    """
    out = StringIO()
    with open(original_file, "r", encoding="utf-8") as pdb:
        remark_done = False
        for line in pdb:
            is_atom = line.startswith(("ATOM", "HETATM"))
            if is_atom and not remark_done:
                out.write(
                    f"REMARK 999  Distances from {source_mer} are stored in the B-factor column\n"
                )
                remark_done = True

            if is_atom and len(line) >= 66:
                res = line[17:20].strip()
                chain = line[21].strip()
                num = line[22:26].strip()
                mer_name = f"{res}-{num}({chain})"
                bf = weights.get(mer_name)
                if bf is not None and math.isfinite(bf):
                    bf = min(bf, 999.99)
                    line = f"{line[:60]}{bf:6.2f}{line[66:]}"
            out.write(line)
    return out.getvalue()


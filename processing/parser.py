"""PDB parsing helpers."""

from __future__ import annotations

from typing import Dict, Iterable

from models import Atom, Mer, Location


def read_input_file(file_path: str) -> Iterable[str]:
    with open(file_path, "r", encoding="utf-8") as file_handle:
        return file_handle.readlines()


def parse_atoms(raw_lines: Iterable[str]) -> Dict[str, Mer]:
    """Create Mer objects and attach Atom objects to them."""
    mers: Dict[str, Mer] = {}
    for line in raw_lines:
        if line.startswith(("ATOM", "HETATM")):
            atom = parse_atom_line(line)
            if atom:
                mers.setdefault(atom.mer.name, atom.mer).add_atom(atom)

    for mer in mers.values():
        mer.calc_com()
    return mers


def parse_atom_line(line: str) -> Atom | None:
    """Return an Atom or None (if line malformed)."""
    try:
        if len(line) < 66:
            return None
        atom_id = int(line[6:11])
        name = line[12:16].strip()
        resname = line[17:20].strip()
        chain = line[21].strip()
        resnum = int(line[22:26])
        x, y, z = map(float, (line[30:38], line[38:46], line[46:54]))
        temp = float(line[60:66])

        loc = Location(x, y, z)
        mer_name = f"{resname}-{resnum}({chain})"
        mer = Mer(mer_name, resname, resnum, chain)
        return Atom(atom_id, name, resname, "", loc, temp, mer)
    except Exception:
        return None


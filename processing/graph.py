"""Graph construction and shortest-path helpers."""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Sequence

from models import Mer, Interaction


def calculate_interactions(mers: Dict[str, Mer]) -> List[Interaction]:
    """Mark bonds (<4.5 Å) and create Interaction objects."""
    mer_list: Sequence[Mer] = list(mers.values())

    for i, src in enumerate(mer_list):
        for j, dst in enumerate(mer_list):
            if i == j:
                continue
            bonded = any(
                s_atom.location.distance_to(d_atom.location) < 4.5
                for s_atom in src.atoms
                for d_atom in dst.atoms
            )
            if bonded:
                src.add_bond(dst)
                dst.add_bond(src)

    interactions: List[Interaction] = []
    for i in range(len(mer_list)):
        for j in range(i + 1, len(mer_list)):
            a, b = mer_list[i], mer_list[j]
            if a.is_bonded_to(b):
                interactions.append(Interaction(a, b))
    return interactions


def build_adjacency_map(mers: Dict[str, Mer]) -> Dict[str, Dict[str, float]]:
    """Return {mer: {nbr: weight}} for every Mer."""
    adj = {m.name: {} for m in mers.values()}
    for a in mers.values():
        for b_name, bond_count in a.bond_count.items():
            if bond_count and b_name in mers:
                b = mers[b_name]
                affinity = bond_count / math.sqrt(len(a.atoms) * len(b.atoms) or 1)
                weight = 1.0 / affinity if affinity else math.inf
                adj[a.name][b_name] = weight
                adj[b_name][a.name] = weight
    return adj


def dijkstra(adj: Dict[str, Dict[str, float]], src: str) -> Dict[str, float]:
    """Return distance map from src."""
    dist = {m: math.inf for m in adj}
    dist[src] = 0.0
    visited = set()

    while (unvisited := {m for m in adj if m not in visited}):
        current = min(unvisited, key=dist.get)
        visited.add(current)
        if dist[current] == math.inf:
            break
        for nbr, weight in adj[current].items():
            if nbr not in visited and dist[current] + weight < dist[nbr]:
                dist[nbr] = dist[current] + weight
    return dist


def find_connected_components(adj: Dict[str, Dict[str, float]]) -> List[set]:
    comps, seen = [], set()
    for node in adj:
        if node in seen:
            continue
        stack, comp = [node], set()
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            comp.add(n)
            stack.extend(adj[n])
        comps.append(comp)
    return comps


def prune_to_component(adj: Dict[str, Dict[str, float]], keep: Iterable[str]):
    keep_set = set(keep)
    return {
        n: {k: w for k, w in nbrs.items() if k in keep_set}
        for n, nbrs in adj.items()
        if n in keep_set
    }


def prune_interactions(interactions: Sequence[Interaction], keep_map: Dict[str, Dict[str, float]]):
    keep_nodes = set(keep_map.keys())
    return [i for i in interactions if i.from_mer in keep_nodes and i.to_mer in keep_nodes]


def prune_mers(mers: Dict[str, Mer], keep_map: Dict[str, Dict[str, float]]):
    return {m: mers[m] for m in keep_map if m in mers}


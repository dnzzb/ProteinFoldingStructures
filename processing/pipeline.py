"""High-level PDB processing pipeline."""

from __future__ import annotations

import math
from typing import Tuple

from .parser import read_input_file, parse_atoms
from .graph import (
    build_adjacency_map,
    calculate_interactions,
    dijkstra,
    find_connected_components,
    prune_interactions,
    prune_mers,
    prune_to_component,
)


def process_pdb_file(file_path: str) -> Tuple:
    """
    Returns:
        best_source_mer, mers, total_weight_sums, interactions,
        all_distance_sums, islands_removed (bool)
    """
    raw = read_input_file(file_path)
    mers = parse_atoms(raw)

    interactions = calculate_interactions(mers)
    adj = build_adjacency_map(mers)

    comps = find_connected_components(adj)
    largest = max(comps, key=len)
    islands_removed = len(comps) > 1

    adj = prune_to_component(adj, largest)
    interactions = prune_interactions(interactions, adj)
    mers = prune_mers(mers, adj)

    all_dist, best_src, min_sum = {}, None, math.inf
    for mer in largest:
        distances = dijkstra(adj, mer)
        all_dist[mer] = distances
        distance_sum = sum(v for v in distances.values() if math.isfinite(v))
        if distance_sum < min_sum:
            best_src, min_sum = mer, distance_sum

    total_weight_sums = dict(all_dist[best_src])
    return best_src, mers, total_weight_sums, interactions, all_dist, islands_removed


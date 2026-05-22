# consistent-hash-simulator

## Why this exists
Consistent hashing is foundational for distributed caches, sharding, and load balancers. Engineers need to understand how node additions, removals, and failures affect key distribution without deploying real clusters.

## Features
- Interactive ring visualization with braille heatmaps
- Configurable virtual nodes and hash functions
- Failure injection and rebalance metrics
- Exportable distribution reports and histograms
- Deterministic simulations for reproducible experiments

## Installation
pip install consistent-hash-simulator

## Usage
consistent-hash-simulator run --nodes 5 --keys 10000 --vnode 128
consistent-hash-simulator visualize --output ring.png

## Benchmarks
Typical run completes 50k key placements in <200ms on M2 MacBook.

## Alternatives considered
ketama, hash_ring, rendezvous hashing libraries — none provide built-in simulation, visualization and failure modeling.
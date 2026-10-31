# hdr-histogram-cli

## Why this exists
High-resolution latency analysis is essential for production systems yet most tools either lose precision at the tail or suffer from coordinated omission. hdr-histogram-cli brings the battle-tested HDR Histogram algorithm to the CLI with first-class support for correction, merging, and export.

## Features
- Record raw or corrected histograms from stdin or files
- Merge multiple histograms while preserving precision
- Query any percentile, mean, max, stddev with sub-microsecond accuracy
- Export to JSON, CSV, or Prometheus text format
- Coordinated omission correction via external interval timestamps
- Progress bars and streaming mode for live ingestion

## Installation
pip install hdr-histogram-cli

## Usage
hdr-histogram-cli record --input latency.log --output dist.hgrm
hdr-histogram-cli query dist.hgrm --percentiles 50,99,99.9

## Benchmarks
Processed 10M samples in <800ms; memory usage <12 MiB for 5-significant-digit precision.

## Alternatives considered
- hdrhistogram (Java) – no Python streaming CLI
- prometheus histograms – fixed buckets, loss of tail fidelity
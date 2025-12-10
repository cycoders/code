# Genetic TSP Solver

A pure Python CLI tool implementing a Genetic Algorithm to solve the Traveling Salesman Problem (TSP). It generates random cities, evolves solutions, and visualizes the best tour order on an ASCII grid.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org)

## Features

- **No external dependencies**: Pure standard library Python.
- **Configurable GA parameters**: Population size, generations, mutation rate, etc.
- **ASCII visualization**: Grid showing city positions labeled A-Z/0-9 in tour order.
- **Progress tracking**: Console output of best fitness per generation.
- **Reproducible**: Seeded random for consistent runs.

## Quick Start

1. Navigate to the project:
   ```bash
   cd genetic-tsp-solver
   ```

2. Run with defaults (12 cities):
   ```bash
   python main.py
   ```

3. Custom run:
   ```bash
   python main.py --num-cities 18 --pop-size 400 --generations 1500 --mutation-rate 0.02
   ```

## Example Output

```
Gen 0: best fitness 0.0085
Gen 100: best fitness 0.0452
...
Best distance: 187.34
Best path: [5, 2, 9, 1, 7, 3, 11, 8, 4, 10, 6, 0]
City positions:
0: [23, 12]
1: [45, 34]
...
.........................
......C..................
..................B......
...............D..E......
.........................
A.......................
........F...G............
......H...I..............
................J........
.....K...................
..............L..........
```

The letters A-L represent the tour order (A→B→C→...→L→A).

## Arguments

| Flag | Default | Description |
|------|---------|-------------|
| `--num-cities` | `12` | Number of cities (≤26 for labels) |
| `--pop-size` | `200` | Population size |
| `--generations` | `1000` | Number of generations |
| `--mutation-rate` | `0.05` | Probability of mutation |
| `--tournament-size` | `3` | Tournament selection size |

## Algorithm

- **Representation**: Permutations of city indices.
- **Fitness**: Inverse total tour distance.
- **Selection**: Tournament.
- **Crossover**: Order Crossover (OX).
- **Mutation**: Random swap.
- **Elitism**: Carry over best individual.

Cities are randomly placed in a 50x50 grid.

## License

MIT. Enjoy evolving optimal tours!
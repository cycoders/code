# ASCII Evo Artist

**Genetic algorithm-powered ASCII art evolver. Watch evolution craft art from random noise!**

Pure Python 3, zero dependencies. Runnable out-of-the-box.

## 🎉 Quick Start

```bash
python ascii-evo-artist/main.py
```

Evolves a tree ASCII art. Prints progress every 20 gens + final best. Saves to `output/best.txt`.

**Target:**
```
   ^   
  ^^^  
 ^^^^^ 
^^^^^^^
  |||  
   |   
```

## 📋 Usage

```bash
python ascii-evo-artist/main.py [OPTIONS]
```

### Options
| Flag | Description | Default |
|------|-------------|---------|
| `--generations, -g &lt;INT&gt;` | Number of generations | 200 |
| `--population-size, -p &lt;INT&gt;` | Population size | 50 |
| `--mutation-rate, -m &lt;FLOAT&gt;` | Per-char mutation prob | 0.01 |
| `--tournament-size, -t &lt;INT&gt;` | Tournament competitors | 3 |
| `--elite-size, -e &lt;INT&gt;` | Elites carried over | 2 |
| `--target-file &lt;PATH&gt;` | Custom target ASCII file | (built-in tree) |
| `--output-file &lt;PATH&gt;` | Save best art | `output/best.txt` |
| `--seed &lt;INT&gt;` | RNG seed for reproducibility | 42 |

## 🎨 Custom Targets

1. Create `my_target.txt`:
```
 *** 
*   *
 ****
*   *
 *** 
```

2. Run:
```bash
python main.py --target-file my_target.txt -g 500 -p 100
```

Uses `examples/tree.txt` as reference.

## 🔬 How It Works

- **Genome**: Flattened string of chars from `' .,:=-+*#%@'`.
- **Density Map**: `{' ':0, '.':1, ',':2, ':':3, '-':4, '=':5, '+':6, '*':7, '#':8, '%':9, '@':10}`.
- **Fitness**: Minimize sum of absolute density diffs to target.
- **Ops**:
  - Tournament selection.
  - Single-point crossover.
  - Per-locus mutation.
  - Elitism.

Tune params: larger pop/gens = better, but slower.

## 📁 Structure

```
ascii-evo-artist/
├── main.py     # Core evolver
├── README.md   # This file
└── examples/
    └── tree.txt # Default target
```

**Pro tip**: `python main.py --seed 0 -g 1000` for wild results!

## 🚀 Author
Elite full-stack dev auto-gen. MIT License.
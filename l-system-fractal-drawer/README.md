# L-System Fractal Drawer

A pure Python CLI tool to generate procedural fractals using Lindenmayer systems (L-systems) and render them as SVG images.

L-systems are parallel string rewriting systems introduced by Aristid Lindenmayer, widely used for modeling plant growth and generating fractals.

## Features

- No external dependencies (pure Python 3.6+)
- Customizable axiom, production rules, angle, iterations, and segment length
- Automatic bounding box calculation, scaling, and centering
- Output to SVG (scalable vector graphics)

## Installation

No installation required. Just run `python main.py`.

## Usage

```
python main.py [OPTIONS] --output OUTPUT.svg
```

### Options

- `--axiom TEXT` (default: `F`): Starting string
- `--rules TEXT` (default: `F:F[+F]F[-F]F`): Comma-separated rules like `F:FF-[-F+F]+F,G:GG`
- `--angle FLOAT` (default: `25.7`): Turn angle in degrees
- `--iterations INTEGER` (default: `5`): Rewriting iterations
- `--step-length FLOAT` (default: `3.0`): Length of each segment
- `--output, -o PATH`: Output SVG file (required)

### Examples

1. **Binary Tree** (default):
   ```bash
   python main.py --output tree.svg --iterations 7 --step-length 2.5
   ```

2. **Koch Snowflake**:
   ```bash
   python main.py --axiom "F--F--F" --rules "F:F+F--F+F" --angle 60 --iterations 4 --step-length 5 --output koch.svg
   ```

3. **Koch Curve**:
   ```bash
   python main.py --axiom "F" --rules "F:F+F--F+F" --angle 60 --iterations 6 --step-length 3 --output koch-curve.svg
   ```

4. **Dragon Curve**:
   ```bash
   python main.py --axiom "FX" --rules "X:X+YF+,Y:-FX-Y,F:F" --angle 90 --iterations 14 --step-length 2 --output dragon.svg
   ```

Higher iterations produce longer strings and more detail but may take time/memory.

## Symbols

- `F`, `G`: Draw forward (move and line)
- `+`: Turn left
- `-`: Turn right
- `[` `]`: Push/pop position and direction to stack

Other characters are ignored (used for non-terminals like `X`, `Y`).

## License

MIT License. See LICENSE for details (add if desired).

Enjoy procedural art!
import argparse
import math

def generate_lsystem(axiom: str, rules: dict[str, str], iterations: int) -> str:
    current = axiom
    for _ in range(iterations):
        current = ''.join(rules.get(c, c) for c in current)
    return current

def draw_lsystem(production: str, angle_deg: float, step_length: float, output_file: str):
    angle = math.radians(angle_deg)
    stack: list[tuple[float, float, float]] = []
    pos_x: float = 0.0
    pos_y: float = 0.0
    dir_angle: float = 0.0
    all_x: list[float] = [0.0]
    all_y: list[float] = [0.0]
    path_d_parts: list[str] = ["M 0 0"]

    for cmd in production:
        if cmd in ('F', 'G'):
            new_x = pos_x + step_length * math.cos(dir_angle)
            new_y = pos_y + step_length * math.sin(dir_angle)
            path_d_parts.append(f"L {new_x} {new_y}")
            all_x.append(new_x)
            all_y.append(new_y)
            pos_x = new_x
            pos_y = new_y
        elif cmd == '+':
            dir_angle += angle
        elif cmd == '-':
            dir_angle -= angle
        elif cmd == '[':
            stack.append((pos_x, pos_y, dir_angle))
        elif cmd == ']':
            if stack:
                pos_x, pos_y, dir_angle = stack.pop()

    # Compute bounds
    min_x = min(all_x)
    max_x = max(all_x)
    min_y = min(all_y)
    max_y = max(all_y)
    width = max_x - min_x if max_x > min_x else 1.0
    height = max_y - min_y if max_y > min_y else 1.0

    # Scale to fit 450x450 with padding
    scale = min(450 / width, 450 / height)
    svg_size = 500
    offset_x = (svg_size - width * scale) / 2
    offset_y = (svg_size - height * scale) / 2

    # Build transformed path data
    start_tx = offset_x + (0 - min_x) * scale
    start_ty = svg_size - (offset_y + (0 - min_y) * scale)
    d = f"M {start_tx:.3f} {start_ty:.3f}"

    for seg in path_d_parts[1:]:
        parts = seg.split()
        x = float(parts[1])
        y = float(parts[2])
        tx = offset_x + (x - min_x) * scale
        ty = svg_size - (offset_y + (y - min_y) * scale)
        d += f" L {tx:.3f} {ty:.3f}"

    svg_content = f'''<svg width="{svg_size}" height="{svg_size}" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="{svg_size}" height="{svg_size}" fill="white"/>
  <path d="{d}" stroke="black" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
</svg>'''

    with open(output_file, 'w') as f:
        f.write(svg_content)
    print(f"Generated SVG saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="L-System Fractal Drawer")
    parser.add_argument('--axiom', default='F', help='Starting axiom (default: F)')
    parser.add_argument('--rules', default='F:F[+F]F[-F]F', help='Rules: key:value,key:value (default: F:F[+F]F[-F]F)')
    parser.add_argument('--angle', type=float, default=25.7, help='Turn angle degrees (default: 25.7)')
    parser.add_argument('--iterations', type=int, default=5, help='Iterations (default: 5)')
    parser.add_argument('--step-length', type=float, default=3.0, help='Segment length (default: 3.0)')
    parser.add_argument('--output', '-o', required=True, help='Output SVG file')

    args = parser.parse_args()

    rule_dict = dict(rule.split(':', 1) for rule in args.rules.split(','))

    production = generate_lsystem(args.axiom, rule_dict, args.iterations)
    print(f"Production string length: {len(production)}")

    draw_lsystem(production, args.angle, args.step_length, args.output)

import os
from pathlib import Path
from typing import List, Tuple
from fontTools import subset
from fontTools.ttLib import TTFont

from rich.progress import Progress

FontStat = Tuple[str, int, int, float, int, int]

def subset_single_font(input_path: Path, codepoints: set[int], output_path: Path) -> FontStat:
    """Subset one font, return stats."""

    font = TTFont(input_path)
    subsetter = subset.Subsetter()
    subsetter.populate(codepoints=list(codepoints))
    subsetter.subset(font)

    orig_size = input_path.stat().st_size
    output_path.parent.mkdir(parents=True, exist_ok=True)
    font.save(output_path)
    sub_size = output_path.stat().st_size

    # Glyph counts
    glyphs_used = len(codepoints & set(font.getBestCmap().keys()))
    glyphs_total = len(font['maxp'].numGlyphs)

    pct = ((orig_size - sub_size) / orig_size * 100) if orig_size else 0

    return (
        input_path.name,
        orig_size,
        sub_size,
        pct,
        glyphs_used,
        glyphs_total,
    )

def subset_fonts(font_paths: List[Path], codepoints: set[int], output_dir: Path) -> List[FontStat]:
    stats = []
    with Progress() as progress:
        task = progress.add_task("[green]Subsetting fonts...", total=len(font_paths))
        for font_path in font_paths:
            try:
                out_path = output_dir / f"{font_path.stem}.subset{font_path.suffix}"
                stat = subset_single_font(font_path, codepoints, out_path)
                stats.append(stat)
                progress.advance(task)
            except Exception as e:
                print(f"Error subsetting {font_path}: {e}")
    return stats
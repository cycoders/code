import io
import logging
import os
import pathlib
from typing import Dict, Any, Tuple
from tqdm import tqdm

import pikepdf
from rich import print as rprint
from rich.logging import RichHandler

import pdf_optimizer_cli.image_optimizer as imgopt

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)


def get_stats(input_path: pathlib.Path, quality: int) -> Dict[str, Any]:
    """Dry-run stats: scan images without modifying."""
    stats = {"images_total": 0, "images_optimized": 0, "bytes_saved": 0}
    try:
        with pikepdf.Pdf.open(input_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                stats.update(_scan_page_images(page, quality))
    except Exception as e:
        rprint(f"[red]Invalid PDF: {e}[/red]")
        raise typer.Exit(1)
    return stats


def _scan_page_images(page, quality: int) -> Dict[str, Any]:
    stats = {"images_total": 0, "images_optimized": 0, "bytes_saved": 0}
    if '/Resources' not in page:
        return stats
    resources = page['/Resources']
    stats.update(_process_resources(resources, quality, scan_only=True))
    return stats


def optimize_pdf(input_path: str, output_path: str, quality: int = 85) -> None:
    """Full optimization pipeline."""
    input_path = pathlib.Path(input_path)
    output_path = pathlib.Path(output_path)

    if not input_path.exists():
        rprint(f"[red]Input file not found: {input_path}[/red]")
        raise typer.Exit(1)

    try:
        with pikepdf.Pdf.open(input_path) as pdf:
            # Subset fonts
            pdf.subset_fonts(recursive=True)
            logger.info("Fonts subsetted")

            # Optimize images recursively
            images_opt = 0
            for page in tqdm(pdf.pages, desc="Pages"):
                if '/Resources' in page:
                    resources = page['/Resources']
                    images_opt += _process_resources(resources, quality)

            logger.info(f"Optimized {images_opt} images")

            # Cleanup & save
            output_path.parent.mkdir(parents=True, exist_ok=True)
            pdf.remove_unreferenced_resources()
            pdf.save(
                output_path,
                linearize=True,
                compress_streams=True,
                object_stream_mode=pikepdf.ObjectStreamMode.generate,
            )
            logger.info(f"Saved to {output_path}")

    except pikepdf.PdfError as e:
        rprint(f"[red]Invalid PDF: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        raise


def _process_resources(resources: pikepdf.Dictionary, quality: int, scan_only: bool = False) -> int:
    """Process XObjects recursively, return num optimized."""
    count = 0
    if '/XObject' not in resources:
        return 0

    xobjs = resources['/XObject']
    for name, xobj in list(xobjs.items()):
        # Image
        if xobj.Type == '/XObject' and xobj.get('/Subtype') == '/Image':
            data = bytes(xobj)
            opt_data, improved = imgopt.optimize_image(data, quality)
            if improved:
                if not scan_only:
                    xobj.Filter = pikepdf.Name.DCTDecode
                    xobj.DecodeParms = pikepdf.Dictionary()
                    xobj.stream = opt_data
                    if '/ColorSpace' not in xobj:
                        xobj.ColorSpace = '/DeviceRGB'
                count += 1

        # Recurse Form
        elif xobj.Type == '/XObject' and xobj.get('/Subtype') == '/Form':
            if '/Resources' in xobj:
                count += _process_resources(xobj['/Resources'], quality, scan_only)

    return count


def batch_optimize(input_dir: str, output_dir: str, quality: int):
    pass  # Handled in CLI

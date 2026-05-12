import pathlib
import pytest
import pikepdf

from pdf_optimizer_cli.optimizer import get_stats, optimize_pdf


def test_get_stats_valid_pdf(tmp_path):
    # Create minimal PDF
    pdf_path = tmp_path / "test.pdf"
    pdf = pikepdf.Pdf.new()
    page = pdf.new_page(612, 792)  # Letter
    pdf.save(pdf_path)

    stats = get_stats(pdf_path, 85)
    assert isinstance(stats, dict)
    assert stats["images_total"] >= 0


def test_optimize_pdf_minimal(tmp_path):
    input_pdf = tmp_path / "input.pdf"
    output_pdf = tmp_path / "output.pdf"
    pdf = pikepdf.Pdf.new()
    pdf.save(input_pdf)

    optimize_pdf(str(input_path), str(output_pdf), 85)
    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0


def test_invalid_pdf(tmp_path):
    invalid = tmp_path / "invalid.pdf"
    invalid.write_bytes(b"%PDF-garbage")
    with pytest.raises(SystemExit):
        get_stats(invalid, 85)

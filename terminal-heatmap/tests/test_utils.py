from terminal_heatmap.utils import value_to_braille, get_intensity_color


def test_value_to_braille() -> None:
    assert value_to_braille(0.0) == chr(0x2800)
    assert value_to_braille(100.0) == chr(0x28FF)
    assert value_to_braille(50.0) == chr(0x287F)
    assert value_to_braille(101.0) == chr(0x28FF)
    assert value_to_braille(-1.0) == chr(0x2800)


def test_get_intensity_color() -> None:
    assert get_intensity_color(0.0) == "blue"
    assert get_intensity_color(4.9) == "blue"
    assert get_intensity_color(5.0) == "green"
    assert get_intensity_color(19.9) == "green"
    assert get_intensity_color(20.0) == "yellow"
    assert get_intensity_color(49.9) == "yellow"
    assert get_intensity_color(50.0) == "red"
    assert get_intensity_color(1000.0) == "red"
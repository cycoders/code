import pytest

from src.cli import create_parser


def test_create_parser():
    parser = create_parser()
    assert parser.prog == "pokemon-info-cli"


def test_parse_no_pokemon():
    parser = create_parser()
    args = parser.parse_args([])
    assert args.pokemon is None
    assert not args.json
    assert not args.sprite


def test_parse_pokemon_name():
    parser = create_parser()
    args = parser.parse_args(["pikachu"])
    assert args.pokemon == "pikachu"


def test_parse_pokemon_id():
    parser = create_parser()
    args = parser.parse_args(["25"])
    assert args.pokemon == "25"


def test_parse_options():
    parser = create_parser()
    args = parser.parse_args(["mewtwo", "-j", "-s"])
    assert args.pokemon == "mewtwo"
    assert args.json
    assert args.sprite

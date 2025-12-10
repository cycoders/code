import pytest

from src.models import pokemon_from_api, Pokemon, PokemonType, Stat


def test_pokemon_from_api():
    data = {
        "name": "pikachu",
        "id": 25,
        "height": 4,
        "weight": 60,
        "types": [
            {"slot": 1, "type": {"name": "electric"}},
        ],
        "stats": [
            {"base_stat": 35, "effort": 0, "stat": {"name": "hp"}},
            {"base_stat": 55, "effort": 0, "stat": {"name": "attack"}},
        ],
        "sprites": {
            "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"
        },
    }
    pkm = pokemon_from_api(data)
    assert pkm.name == "pikachu"
    assert pkm.id == 25
    assert pkm.height == 4
    assert pkm.weight == 60
    assert len(pkm.types) == 1
    assert pkm.types[0].name == "electric"
    assert len(pkm.stats) == 2
    assert pkm.stats[0].name == "hp"
    assert pkm.stats[0].base_stat == 35
    assert pkm.stats[1].name == "attack"
    assert pkm.stats[1].base_stat == 55
    assert (
        pkm.sprite_url
        == "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"
    )


def test_pokemon_from_api_missing_fields():
    data = {"name": "missingno", "id": 0, "height": 0, "weight": 0}
    pkm = pokemon_from_api(data)
    assert pkm.types == []
    assert pkm.stats == []
    assert pkm.sprite_url == ""

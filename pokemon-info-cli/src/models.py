from dataclasses import dataclass

from typing import List, Dict, Any


@dataclass
class PokemonType:
    name: str


@dataclass
class Stat:
    name: str
    base_stat: int


@dataclass
class Pokemon:
    name: str
    id: int  # noqa: A003
    height: int
    weight: int
    types: List[PokemonType]
    stats: List[Stat]
    sprite_url: str


def pokemon_from_api(data: Dict[str, Any]) -> Pokemon:
    types = [PokemonType(t["type"]["name"]) for t in data.get("types", [])]
    stats = [Stat(s["stat"]["name"], s["base_stat"]) for s in data.get("stats", [])]
    sprites = data.get("sprites", {})
    sprite_url = sprites.get("front_default", "")
    return Pokemon(
        data["name"],
        data["id"],
        data["height"],
        data["weight"],
        types,
        stats,
        sprite_url,
    )

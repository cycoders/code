import argparse
import json

from dataclasses import asdict

from .api import fetch_pokemon

from .models import Pokemon


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pokemon-info-cli",
        description="A CLI tool to fetch Pokemon details from PokeAPI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\nExamples:\n  %(prog)s pikachu\n  %(prog)s 25 --json\n  %(prog)s mewtwo --sprite\n        """,
    )
    parser.add_argument(
        "pokemon",
        nargs="?",
        help='Pokemon name (e.g. "pikachu") or ID (e.g. "25")',
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="Output full JSON data instead of formatted",
    )
    parser.add_argument(
        "-s",
        "--sprite",
        action="store_true",
        help="Print the front sprite URL",
    )
    return parser


def run():
    parser = create_parser()
    args = parser.parse_args()
    if args.pokemon is None:
        parser.print_help()
        return
    pokemon = fetch_pokemon(args.pokemon)
    if args.json:
        print(json.dumps(asdict(pokemon), indent=2))
    else:
        print(f"#{pokemon.id:03d} {pokemon.name.title()}")
        print(f"Height: {pokemon.height / 10:.1f} m ({pokemon.height} dm)")
        print(f"Weight: {pokemon.weight / 10:.1f} kg ({pokemon.weight} hg)")
        print("Types: " + " / ".join(t.name.title() for t in pokemon.types))
        print("\nBase Stats:")
        for stat in pokemon.stats:
            stat_name = stat.name.replace("-", " ").title()
            print(f"  {stat_name:<15}: {stat.base_stat}")
    if args.sprite:
        print(f"\nSprite: {pokemon.sprite_url}")

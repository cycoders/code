import json
import sys
import urllib.error
import urllib.request

from .models import pokemon_from_api, Pokemon


def fetch_pokemon(name_or_id: str) -> Pokemon:
    url = f"https://pokeapi.co/api/v2/pokemon/{name_or_id.lower()}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
        return pokemon_from_api(data)
    except urllib.error.HTTPError as e:
        print(
            f"Error: Pokemon '{name_or_id}' not found or API error (HTTP {e.code}).",
            file=sys.stderr,
        )
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid response from API.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

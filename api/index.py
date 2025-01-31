from api.module import get_xp_by_github, get_pokemon, get_svg_banner
from flask import Flask, request, Response
from dotenv import load_dotenv
from cache import get_from_cache, save_to_cache

load_dotenv("./infra/envs/.env")
app = Flask(__name__)

@app.route('/')
def render():
    args = request.args
    user = args.get("user") or "CriticalNoob02"
    pokemon = args.get("pokemon") or "charmander"
    theme = args.get("theme") or "charmander"

    cache_key = f"{user}-{pokemon}-{theme}"
    cached_data = get_from_cache(cache_key)

    if cached_data:
        print(f"Servindo do cache: {cache_key}")
        return Response(cached_data, mimetype='image/svg+xml')

    print(f"Gerando novo SVG para {cache_key}")
    xp = get_xp_by_github(user)
    pokeDTO = get_pokemon(pokemon, xp)
    svg_content = get_svg_banner(pokeDTO, theme)

    save_to_cache(cache_key, svg_content)

    return Response(svg_content, mimetype='image/svg+xml')

if __name__ == "__main__":
    app.run(debug=True)

from api.module import get_xp_by_github, get_pokemon, get_svg_banner
from flask import Flask, request, Response
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import json

load_dotenv("./infra/envs/.env")
app = Flask(__name__)

CACHE_FILE = "cache.json"
CACHE_EXPIRATION = timedelta(hours=24)

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_cache(cache_data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=4)

CACHE = load_cache()

@app.route('/')
def render():
    args = request.args
    user = args.get("user") or "CriticalNoob02"
    pokemon = args.get("pokemon") or "charmander"
    theme = args.get("theme") or "charmander"

    cache_key = f"{user}-{pokemon}-{theme}"

    if cache_key in CACHE:
        cached_data = CACHE[cache_key]
        if datetime.utcnow() < datetime.fromisoformat(cached_data["expires_at"]):
            print(f"Servindo do cache: {cache_key}")
            return Response(cached_data["svg"], mimetype='image/svg+xml')

    print(f"Gerando novo SVG para {cache_key}")
    xp = get_xp_by_github(user)
    pokeDTO = get_pokemon(pokemon, xp)
    svg_content = get_svg_banner(pokeDTO, theme)

    CACHE[cache_key] = {
        "svg": svg_content,
        "expires_at": (datetime.utcnow() + CACHE_EXPIRATION).isoformat()
    }
    save_cache(CACHE)

    return Response(svg_content, mimetype='image/svg+xml')

# Handler para o Vercel
def handler(request):
    with app.request_context(request):
        return app.full_dispatch_request()

if __name__ == "__main__":
    app.run(debug=True)

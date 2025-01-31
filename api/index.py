from api.module import get_xp_by_github, get_pokemon, get_svg_banner
from flask import Flask, request, Response
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv("./infra/envs/.env")
app = Flask(__name__)

# Cache em memória
CACHE = {}
CACHE_EXPIRATION = timedelta(hours=24)  

@app.route('/')
def render():
    args = request.args
    user = args.get("user") or "CriticalNoob02"
    pokemon = args.get("pokemon") or "charmander"
    theme = args.get("theme") or "charmander"

    # Criar uma chave única para armazenar no cache (baseada nos parâmetros)
    cache_key = f"{user}-{pokemon}-{theme}"

    # Verifica se já temos o resultado armazenado e se o cache ainda é válido
    if cache_key in CACHE:
        cached_data = CACHE[cache_key]
        if datetime.utcnow() < cached_data["expires_at"]:
            print(f"Servindo do cache: {cache_key}")
            return Response(cached_data["svg"], mimetype='image/svg+xml')

    # Se não tiver no cache, busca os dados e armazena novamente
    print(f"Gerando novo SVG para {cache_key}")
    xp = get_xp_by_github(user)
    pokeDTO = get_pokemon(pokemon, xp)
    svg_content = get_svg_banner(pokeDTO, theme)

    # Armazena no cache
    CACHE[cache_key] = {
        "svg": svg_content,
        "expires_at": datetime.utcnow() + CACHE_EXPIRATION
    }

    return Response(svg_content, mimetype='image/svg+xml')

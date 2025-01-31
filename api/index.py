from api.module import get_xp_by_github, get_pokemon, get_svg_banner
from flask import Flask, request, Response
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
import os

load_dotenv("./infra/envs/.env")
app = Flask(__name__)

# Configuração do cache
CACHE_FILE = "cache.json"
CACHE_EXPIRATION = timedelta(hours=24)  

# Função para carregar cache do arquivo
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

# Função para salvar cache no arquivo
def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(CACHE, f)

CACHE = load_cache()

@app.route('/')
def render():
    args = request.args
    user = args.get("user") or "CriticalNoob02"
    pokemon = args.get("pokemon") or "charmander"
    theme = args.get("theme") or "charmander"

    cache_key = f"{user}-{pokemon}-{theme}"

    # Verifica se já temos o resultado armazenado e se o cache ainda é válido
    if cache_key in CACHE:
        cached_data = CACHE[cache_key]
        if datetime.utcnow().timestamp() < cached_data["expires_at"]:
            print(f"🔍 Servindo do cache: {cache_key}")
            return Response(cached_data["svg"], mimetype='image/svg+xml')

    print(f"⚡ Gerando novo SVG para {cache_key}")
    
    # Captura erros da API do GitHub
    try:
        xp = get_xp_by_github(user)
    except Exception as e:
        print(f"❌ Erro ao buscar XP no GitHub: {e}")
        return Response("Erro ao buscar dados do GitHub", status=500)

    pokeDTO = get_pokemon(pokemon, xp)
    svg_content = get_svg_banner(pokeDTO, theme)

    # Armazena no cache e salva no arquivo
    CACHE[cache_key] = {
        "svg": svg_content,
        "expires_at": (datetime.utcnow() + CACHE_EXPIRATION).timestamp()
    }
    save_cache()

    return Response(svg_content, mimetype='image/svg+xml')

if __name__ == "__main__":
    app.run(debug=True)

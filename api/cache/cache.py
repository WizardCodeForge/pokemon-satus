import os
from upstash_redis import Redis

# Se a variável de ambiente não estiver configurada, use as credenciais diretamente (não recomendado para produção)
redis_url = os.getenv("KV_REST_API_URL")
if not redis_url:
    # Use as credenciais diretamente, mas tenha cuidado, pois não é seguro colocar tokens dessa forma em produção
    redis_url = "https://key-guinea-46924.upstash.io"
    redis_token = "AbdMAAIjcDE4NjlmNjMyNzdkMmU0MDVhYTY3NTUxODEwMjA1ZmNiNXAxMA"

# Conectando ao Redis usando a URL e o token
redis_client = Redis(url=redis_url, token=redis_token)

def get_from_cache(key):
    """Tenta recuperar o cache do Redis"""
    cached_data = redis_client.get(key)
    if cached_data:
        return cached_data.decode("utf-8")
    return None

def save_to_cache(key, value, expire=86400):
    """Salva no Redis com tempo de expiração (padrão: 1 dia)"""
    redis_client.set(key, value, ex=expire)

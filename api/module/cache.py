import os
import redis

redis_client = redis.Redis.from_url(os.getenv("KV_REST_API_URL"))

def get_from_cache(key):
    """Tenta recuperar o cache do Redis"""
    cached_data = redis_client.get(key)
    if cached_data:
        return cached_data.decode("utf-8")
    return None

def save_to_cache(key, value, expire=86400):
    """Salva no Redis com tempo de expiração (padrão: 1 dia)"""
    redis_client.set(key, value, ex=expire)

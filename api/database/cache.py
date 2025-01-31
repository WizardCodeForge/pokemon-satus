import sqlite3
from datetime import datetime, timedelta

DB_PATH = "cache.db"
CACHE_EXPIRATION_HOURS = 24

def init_db():
    """Cria a tabela no SQLite caso não exista."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT,
            expires_at TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_from_cache(cache_key):
    """Busca um valor no cache se ainda estiver válido."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT value, expires_at FROM cache WHERE key = ?", (cache_key,))
    row = cursor.fetchone()
    conn.close()

    if row:
        value, expires_at = row
        if datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S") > datetime.utcnow():
            return value  # Retorna o SVG armazenado
    
    return None  # Cache expirado ou não encontrado

def save_to_cache(cache_key, value):
    """Salva um novo valor no cache."""
    expires_at = datetime.utcnow() + timedelta(hours=CACHE_EXPIRATION_HOURS)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
        (cache_key, value, expires_at.strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

# Garante que o banco seja inicializado ao importar este módulo
init_db()

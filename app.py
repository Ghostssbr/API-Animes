from flask import Flask, jsonify, request
from scraper import get_recent_animes, get_anime_details
from functools import lru_cache, wraps
from datetime import datetime, timedelta

app = Flask(__name__)

# Decorador de cache com expiração
def timed_lru_cache(seconds: int, maxsize: int = 32):
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime
            return func(*args, **kwargs)
        return wrapped_func
    return wrapper_cache

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "routes": {
            "/recent": "Últimos lançamentos (add ?page=2)",
            "/anime/<id>": "Detalhes do anime"
        }
    })

@app.route('/recent')
@timed_lru_cache(seconds=300)  # Cache de 5 minutos
def recent():
    try:
        page = int(request.args.get('page', 1))
        return jsonify({
            "status": "success",
            "data": get_recent_animes(page)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/anime/<anime_id>')
def anime(anime_id):
    try:
        return jsonify({
            "status": "success",
            "data": get_anime_details(anime_id)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

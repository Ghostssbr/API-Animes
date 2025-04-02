from flask import Flask, jsonify, request
from scraper import get_recent_animes, get_anime_details
import time
from functools import lru_cache

app = Flask(__name__)

# Cache de 5 minutos para evitar sobrecarregar o site
@lru_cache(maxsize=32, ttl=300)
def cached_recent_animes(page=1):
    return get_recent_animes(page)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "endpoints": {
            "/recent": "Últimos lançamentos",
            "/anime/<id>": "Detalhes do anime"
        },
        "repo": "github.com/seuuser/animefire-api"
    })

@app.route('/recent')
def recent():
    page = request.args.get('page', default=1, type=int)
    try:
        data = cached_recent_animes(page)
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/anime/<anime_id>')
def anime(anime_id):
    try:
        data = get_anime_details(anime_id)
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
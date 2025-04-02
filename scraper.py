import requests
from bs4 import BeautifulSoup
import hashlib
from urllib.parse import urljoin

BASE_URL = "https://animefire.plus"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Referer': BASE_URL
}

# Cache simples de animes
anime_cache = {}

def generate_id(text):
    return hashlib.md5(text.encode()).hexdigest()[:8]

def get_recent_animes(page=1):
    url = f"{BASE_URL}/animes-lancamentos/{page}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        animes = []
        
        for item in soup.select('div.divCardUltimosEps'):
            title = item.select_one('h3.animeTitle').get_text(strip=True)
            image = item.select_one('img')['src']
            link = urljoin(BASE_URL, item.select_one('a')['href'])
            
            anime_id = generate_id(title)
            anime_cache[anime_id] = link
            
            animes.append({
                'id': anime_id,
                'title': title,
                'image': image,
                'url': link
            })
        
        return animes
    except Exception as e:
        raise Exception(f"Erro ao buscar animes: {str(e)}")

def get_anime_details(anime_id):
    if anime_id not in anime_cache:
        raise Exception("Anime não encontrado no cache")
    
    try:
        url = anime_cache[anime_id]
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        episodes = []
        
        for ep in soup.select('.div_video_list a.lEp')[:10]:  # Limite de 10 episódios
            ep_title = ep.get_text(strip=True)
            ep_url = urljoin(BASE_URL, ep['href'])
            
            episodes.append({
                'title': ep_title,
                'url': ep_url
            })
        
        return {
            'info': {
                'id': anime_id,
                'url': url
            },
            'episodes': episodes
        }
    except Exception as e:
        raise Exception(f"Erro ao buscar detalhes: {str(e)}")

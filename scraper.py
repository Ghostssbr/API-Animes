import cloudscraper
from bs4 import BeautifulSoup
import hashlib
import random
import time
from urllib.parse import urljoin
from functools import lru_cache

# Configurações
BASE_URL = "https://animefire.plus"
REQUEST_DELAY = (1, 3)  # Delay aleatório entre 1-3 segundos
MAX_RETRIES = 3

# Cloudscraper configurado para bypass de proteções
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    },
    delay=10
)

# Headers personalizados
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': BASE_URL,
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1'
}

def generate_id(text):
    """Gera ID único para cada anime"""
    return hashlib.md5(text.encode()).hexdigest()[:8]

def make_request(url):
    """Faz requisições com tratamento de erros e retry"""
    for attempt in range(MAX_RETRIES):
        try:
            time.sleep(random.uniform(*REQUEST_DELAY))
            response = scraper.get(url, headers=HEADERS)
            
            # Verifica se foi bloqueado
            if response.status_code == 403:
                raise Exception("Bloqueado pelo servidor (403)")
            if "cloudflare" in response.text.lower():
                raise Exception("Desafio Cloudflare detectado")
                
            response.raise_for_status()
            return response
            
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise Exception(f"Falha após {MAX_RETRIES} tentativas: {str(e)}")
            time.sleep(2 ** attempt)  # Backoff exponencial

@lru_cache(maxsize=32)
def get_recent_animes(page=1):
    """Busca os últimos animes lançados"""
    try:
        url = f"{BASE_URL}/animes-lancamentos/{page}"
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        animes = []
        for item in soup.select('div.divCardUltimosEps'):
            try:
                title = item.select_one('h3.animeTitle').get_text(strip=True)
                image = item.select_one('img')['src'] or item.select_one('img')['data-src']
                link = urljoin(BASE_URL, item.select_one('a')['href'])
                
                animes.append({
                    'id': generate_id(title),
                    'title': title,
                    'image': image,
                    'url': link,
                    'episodes': get_episode_count(link)  # Função auxiliar
                })
            except Exception as e:
                print(f"Erro ao processar item: {str(e)}")
                continue
        
        return animes[:15]  # Limita a 15 resultados
        
    except Exception as e:
        raise Exception(f"Erro ao buscar animes recentes: {str(e)}")

def get_episode_count(anime_url):
    """Conta o número de episódios disponíveis"""
    try:
        response = make_request(anime_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return len(soup.select('.div_video_list a.lEp'))
    except:
        return 0

def get_episodes(anime_url, limit=10):
    """Busca episódios de um anime específico"""
    try:
        response = make_request(anime_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        episodes = []
        for ep in soup.select('.div_video_list a.lEp')[:limit]:
            try:
                ep_url = urljoin(BASE_URL, ep['href'])
                episodes.append({
                    'title': ep.get_text(strip=True),
                    'url': ep_url,
                    'video_url': extract_video_url(ep_url)  # Função avançada
                })
            except Exception as e:
                print(f"Erro ao processar episódio: {str(e)}")
                continue
        
        return episodes
    except Exception as e:
        raise Exception(f"Erro ao buscar episódios: {str(e)}")

def extract_video_url(episode_url):
    """Extrai URL do vídeo (requer análise adicional)"""
    try:
        response = make_request(episode_url)
        # Implemente a extração real conforme a estrutura do site
        return "https://example.com/video.mp4"  # Placeholder
    except Exception as e:
        raise Exception(f"Erro ao extrair vídeo: {str(e)}")

# Função auxiliar para cache
@lru_cache(maxsize=100)
def get_anime_details(anime_id):
    """Obtém detalhes completos com cache"""
    # Implemente conforme necessário
    return {}

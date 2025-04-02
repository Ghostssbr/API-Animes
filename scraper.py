import cloudscraper
from bs4 import BeautifulSoup
import hashlib
from urllib.parse import urljoin
import time

BASE_URL = "https://animefire.plus"
scraper = cloudscraper.create_scraper()  # Cloudscraper configurado

def generate_id(text):
    return hashlib.md5(text.encode()).hexdigest()[:8]

def get_recent_animes(page=1):
    url = f"{BASE_URL}/animes-lancamentos/{page}"
    try:
        # Adiciona delay para evitar bloqueio
        time.sleep(2)
        
        response = scraper.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        animes = []
        
        for item in soup.select('div.divCardUltimosEps')[:15]:  # Limite de 15 itens
            try:
                title = item.select_one('h3.animeTitle').get_text(strip=True)
                image = item.select_one('img')['src']
                link = urljoin(BASE_URL, item.select_one('a')['href'])
                
                animes.append({
                    'id': generate_id(title),
                    'title': title,
                    'image': image,
                    'url': link
                })
            except Exception as e:
                print(f"Erro ao processar item: {str(e)}")
                continue
        
        return animes
    except Exception as e:
        raise Exception(f"Erro ao buscar animes: {str(e)}")

def get_anime_details(anime_url):
    try:
        time.sleep(1)  # Delay adicional
        response = scraper.get(anime_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Implemente a extração de episódios conforme necessário
        return {"episodes": []}
    except Exception as e:
        raise Exception(f"Erro ao buscar detalhes: {str(e)}")

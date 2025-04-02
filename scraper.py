import cloudscraper
from bs4 import BeautifulSoup
import hashlib
import random
import time
from urllib.parse import urljoin

# Configurações avançadas
BASE_URL = "https://animefire.plus"
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
]

# Configure o Cloudscraper com opções avançadas
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    },
    delay=10,
    interpreter='nodejs'
)

def get_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': BASE_URL,
        'DNT': '1'
    }

def get_recent_animes(page=1):
    url = f"{BASE_URL}/animes-lancamentos/{page}"
    try:
        # Delay aleatório entre 5-15 segundos
        time.sleep(random.randint(5, 15))
        
        response = scraper.get(url, headers=get_random_headers())
        
        # Verifica se foi redirecionado para página de bloqueio
        if "bloqueio" in response.text.lower():
            raise Exception("Site está retornando página de bloqueio")
        
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        animes = []
        
        for item in soup.select('div.divCardUltimosEps'):
            try:
                title = item.select_one('h3.animeTitle').get_text(strip=True)
                image = item.select_one('img')['src']
                link = urljoin(BASE_URL, item.select_one('a')['href'])
                
                animes.append({
                    'id': hashlib.md5(title.encode()).hexdigest()[:8],
                    'title': title,
                    'image': image,
                    'url': link
                })
            except Exception as e:
                print(f"Erro ao processar item: {str(e)}")
                continue
        
        return animes[:12]  # Limita a 12 resultados
    
    except Exception as e:
        print(f"Erro detalhado: {str(e)}")
        raise Exception(f"Falha ao acessar o AnimeFire. Tente novamente mais tarde.")

# ... (mantenha o resto do código)

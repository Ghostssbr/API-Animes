from flask import Flask, jsonify
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import random
import time
import os

app = Flask(__name__)

# Configurações globais
BASE_URL = "https://animefire.plus"
MIN_DELAY = 1  # segundos
MAX_DELAY = 3  # segundos

class AnimeScraper:
    def __init__(self):
        self.driver = self._init_driver()
    
    def _init_driver(self):
        options = uc.ChromeOptions()
        
        if os.getenv('RENDER'):  # Config para produção
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
        
        options.add_argument('--disable-blink-features=AutomationControlled')
        return uc.Chrome(options=options)

    def scrape_recent(self):
        try:
            # Adiciona delay aleatório
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            time.sleep(delay)
            
            # Acessa a página
            self.driver.get(f"{BASE_URL}/animes-lancamentos/1")
            
            # Espera o carregamento
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.divCardUltimosEps"))
            
            # Scroll para simular comportamento humano
            self.driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(0.5)
            
            # Parse do conteúdo
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            results = []
            
            for item in soup.select('div.divCardUltimosEps')[:10]:  # Limite de 10 itens
                try:
                    title = item.select_one('h3.animeTitle').get_text(strip=True)
                    image = item.select_one('img').get('src', '')
                    link = item.select_one('a').get('href', '')
                    
                    if link and not link.startswith('http'):
                        link = f"{BASE_URL}{link}"
                    
                    results.append({
                        'title': title,
                        'image': image,
                        'url': link
                    })
                except Exception as e:
                    print(f"Erro ao processar item: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            raise Exception(f"Erro durante scraping: {str(e)}")
        finally:
            self.driver.quit()

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "endpoints": {
            "/recent": "Últimos lançamentos"
        }
    })

@app.route('/recent')
def recent_animes():
    try:
        scraper = AnimeScraper()
        data = scraper.scrape_recent()
        return jsonify({
            "status": "success",
            "count": len(data),
            "data": data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Configuração para o Gunicorn
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

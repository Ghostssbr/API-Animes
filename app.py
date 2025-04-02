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

# Configuração global
BASE_URL = "https://animefire.plus"
REQUEST_DELAY = (1, 3)  # Delay entre 1-3 segundos

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
            self.driver.get(f"{BASE_URL}/animes-lancamentos/1")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.divCardUltimosEps"))
            
            # Comportamento humano
            time.sleep(random.uniform(*REQUEST_DELAY))
            self.driver.execute_script("window.scrollBy(0, 500);")
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            return [
                {
                    "title": item.select_one('h3.animeTitle').get_text(strip=True),
                    "image": item.select_one('img')['src'],
                    "url": f"{BASE_URL}{item.select_one('a')['href']}"
                }
                for item in soup.select('div.divCardUltimosEps')[:10]  # Limite de 10
            ]
        finally:
            self.driver.quit()

@app.route('/')
def home():
    return jsonify({"status": "online", "routes": ["/recent"]})

@app.route('/recent')
def recent():
    try:
        scraper = AnimeScraper()
        return jsonify({
            "status": "success",
            "data": scraper.scrape_recent()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Para o Gunicorn
application = app

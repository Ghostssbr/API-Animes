import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import random
import json
from bs4 import BeautifulSoup

class AnimeFireScraper:
    def __init__(self):
        self.BASE_URL = "https://animefire.plus"
        self.setup_driver()
        
    def setup_driver(self):
        """Configura o WebDriver com opções stealth"""
        options = uc.ChromeOptions()
        
        # Configurações para o Render.com
        if os.getenv('RENDER'):
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
        
        # Configurações comuns
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'user-agent={self.get_random_user_agent()}')
        
        self.driver = uc.Chrome(
            options=options,
            version_main=114  # Altere para a versão do seu Chrome
        )
        self.driver.set_page_load_timeout(30)

    def get_random_user_agent(self):
        """Rotaciona User-Agents"""
        user_agents = [
            # Lista de 10 user-agents modernos
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            # Adicione mais user-agents aqui
        ]
        return random.choice(user_agents)

    def human_like_interaction(self):
        """Simula comportamento humano"""
        time.sleep(random.uniform(1, 3))
        if random.random() > 0.7:
            self.driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(0.5)

    def get_recent_animes(self, page=1):
        try:
            url = f"{self.BASE_URL}/animes-lancamentos/{page}"
            self.driver.get(url)
            
            # Espera carregar dinamicamente
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.divCardUltimosEps"))
            
            self.human_like_interaction()
            
            # Extrai dados do DOM
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            animes = []
            
            for item in soup.select('div.divCardUltimosEps')[:10]:  # Limite de 10 itens
                try:
                    title = item.select_one('h3.animeTitle').get_text(strip=True)
                    image = item.select_one('img').get('src', '')
                    link = item.select_one('a').get('href', '')
                    
                    if not link.startswith('http'):
                        link = f"{self.BASE_URL}{link}"
                    
                    animes.append({
                        'title': title,
                        'image': image,
                        'url': link
                    })
                except Exception as e:
                    continue
            
            return animes
            
        except Exception as e:
            raise Exception(f"Erro no scraping: {str(e)}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Limpeza segura"""
        try:
            self.driver.quit()
        except:
            pass

# Uso:
# scraper = AnimeFireScraper()
# animes = scraper.get_recent_animes()

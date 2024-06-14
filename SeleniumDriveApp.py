from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Configura il WebDriver di Selenium
options = Options()
options.add_argument("--headless")  # Esegui il browser in modalità headless (senza interfaccia grafica)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL della pagina da cui vuoi estrarre i dati
url = "file:///Users/kevin.malachin/Documents/SupportScopeSheets&HTML/Dior.html"

# Carica la pagina con Selenium
driver.get(url)

# Ottieni il contenuto HTML dopo il rendering dinamico
website_content = driver.page_source

# Chiudi il WebDriver di Selenium
driver.quit()

# Crea l'oggetto BeautifulSoup
soup = BeautifulSoup(website_content, 'html.parser')

# Trova tutti i tag <a> con le classi specificate
classToFind = soup.find_all('a', class_='sc-csuQGl fgtqry')

# Estrai e stampa i testi di ogni tag trovato
for tag in classToFind:
    print(tag.get_text())

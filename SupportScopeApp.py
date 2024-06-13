from bs4 import BeautifulSoup

# Inserisci il percorso del tuo file HTML locale
file_path = '/Users/kevin.malachin/Documents/SupportScopeSheets&HTML/Bouygues.html'

# Leggi il contenuto del file HTML
with open(file_path, 'r', encoding='utf-8') as file:
    website_content = file.read()

# Crea l'oggetto BeautifulSoup
soup = BeautifulSoup(website_content, 'html.parser')

# Trova tutti i tag <a> con le classi specificate
classToFind = soup.find_all('a', class_='sc-csuQGl fgtqry')

# Stampa il contenuto HTML in un formato leggibile (opzionale)
print(soup.prettify())

# Estrai e stampa i testi di ogni tag trovato
for tag in classToFind:
    print(tag.get_text())

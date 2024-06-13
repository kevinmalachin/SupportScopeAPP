import pandas as pd
from bs4 import BeautifulSoup

def main():
    # Percorso del file HTML locale
    html_file_path = r'C:\Users\kevin\Documents\Automatizzazioni\Bouygues.html'
    
    # Percorso del file Excel locale
    excel_file_path = r'C:\Users\kevin\Documents\Automatizzazioni\Bouygues.xlsx'

    # Leggi il contenuto del file HTML
    with open(html_file_path, 'r', encoding='utf-8') as file:
        website_content = file.read()

    # Crea l'oggetto BeautifulSoup
    soup = BeautifulSoup(website_content, 'html.parser')

    # Trova tutti i tag <a> con le classi specificate
    classToFind = soup.find_all('a', class_='sc-csuQGl fgtqry')

    # Estrai i testi di ogni tag trovato
    html_texts = {tag.get_text().strip() for tag in classToFind}  # Utilizzo di un set per i testi HTML

    # Leggi il file Excel
    df = pd.read_excel(excel_file_path, sheet_name='APIs Scope')

    # Chiedi all'utente di inserire il nome del progetto da cercare nella colonna "Project"
    project_name = input("Inserisci il nome del progetto (es. KAM): ").strip()

    # Filtra il DataFrame per il valore specificato nella colonna "Project"
    filtered_df = df[df['Project'] == project_name]

    # Estrai i valori della colonna "APIs Name" dal DataFrame filtrato
    excel_values = {name.strip() for name in filtered_df['APIs Name'].tolist()}  # Utilizzo di un set per i valori Excel

    # Trova i nomi che sono presenti solo nell'HTML o solo nel file Excel filtrato
    unique_names = html_texts.difference(excel_values)

    # Stampa i nomi unici trovati
    print(f"Nomi unici trovati nel progetto '{project_name}':")
    for name in unique_names:
        print(name)

if __name__ == "__main__":
    main()

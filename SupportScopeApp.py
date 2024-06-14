import pandas as pd
from bs4 import BeautifulSoup
import re

def read_html_content(html_file_path):
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            website_content = file.read()
        return website_content
    except FileNotFoundError:
        print(f"File HTML non trovato: {html_file_path}")
        return None
    except Exception as e:
        print(f"Errore durante la lettura del file HTML: {e}")
        return None

def normalize_name(name):
    # Rimuove eventuali suffissi di ambiente e versioni
    return re.sub(r'-(qa|staging|stagging|recette|test|prod)-.*$', '', name.strip().lower())

def find_column_with_value(df, value):
    for column in df.columns:
        if df[column].astype(str).eq(value).any():
            return column
    return None

def read_excel_file(file_path):
    engines = ['openpyxl', 'xlrd', 'odf', 'pyxlsb']
    for engine in engines:
        try:
            return pd.read_excel(file_path, sheet_name='APIs Scope', engine=engine)
        except Exception as e:
            print(f"Errore con il motore {engine}: {e}")
    return None

def extract_runtime_version_from_html(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        runtime_versions = []

        # Trova tutti gli span con attributo data-testid
        spans = soup.find_all('span', {'data-testid': True})
        
        # Estrai il testo contenuto in ciascuno span trovato
        for span in spans:
            runtime_versions.append(span.text.strip())

        return soup, runtime_versions
    
    except Exception as e:
        print(f"Errore durante l'estrazione della versione di runtime dall'HTML: {e}")
        return None, None

def main():
    html_file_path = r'C:\Users\kevin\Documents\Automatizzazioni\FSTR_PROD.html'
    excel_file_path = r'C:\Users\kevin\Documents\Automatizzazioni\FSTR.xlsx'

    website_content = read_html_content(html_file_path)
    if website_content is None:
        return

    soup, runtime_versions_html = extract_runtime_version_from_html(website_content)
    if runtime_versions_html is None or not runtime_versions_html:
        print("Tag di versione di runtime non trovato nell'HTML.")
        print("Versione di runtime non trovata nell'HTML. Impossibile procedere con il confronto.")
        return

    df = read_excel_file(excel_file_path)
    if df is None:
        print(f"Errore durante la lettura del file Excel: {excel_file_path}")
        return

    project_name = input("Inserisci il nome del progetto (es. KAM) o premi invio per saltare il controllo: ").strip()

    if project_name:
        project_column = find_column_with_value(df, project_name)
        if project_column is None:
            print(f"Il progetto '{project_name}' non è stato trovato in nessuna colonna.")
            return

        filtered_df = df[df[project_column].astype(str) == project_name]
        project_apps = {name.strip().lower() for name in filtered_df['APIs Name'].dropna()}
    else:
        project_apps = {name.strip().lower() for name in df['APIs Name'].dropna()}

    print(f"Nomi delle applicazioni per il progetto '{project_name if project_name else 'Non specificato'}':")
    for name in project_apps:
        print(name)

    # Dizionari per mappare nomi normalizzati a nomi originali
    normalized_html_texts = {}
    for name in project_apps:
        normalized_name = normalize_name(name)
        normalized_html_texts.setdefault(normalized_name, set()).add(name)

    # Controllo con HTML
    discrepancies = set()
    for norm_name, original_names in normalized_html_texts.items():
        # Controlla la versione di runtime per ogni applicazione
        for app_name in original_names:
            # Estrai la versione di runtime corrispondente dall'HTML
            runtime_version_html = None
            for span in soup.find_all('span', {'data-testid': True}):
                if app_name in span.text.strip().lower():
                    runtime_version_html = span.text.strip()
                    break
            
            if runtime_version_html is None:
                print(f"Versione di runtime non trovata per l'applicazione '{app_name}' nell'HTML.")
                discrepancies.add(app_name)
            else:
                # Trova la versione di runtime corrispondente nell'Excel
                runtime_version_excel = df.loc[df['APIs Name'].str.lower() == app_name]['Runtime Version'].iloc[0]

                if runtime_version_html.strip() != runtime_version_excel.strip():
                    discrepancies.add(app_name)

    if discrepancies:
        print(f"\nDiscrepanze nelle versioni di runtime tra HTML e Excel per il progetto '{project_name if project_name else 'Non specificato'}':")
        for name in discrepancies:
            print(name)
    else:
        print(f"\nNessuna discrepanza nelle versioni di runtime tra HTML e Excel per il progetto '{project_name if project_name else 'Non specificato'}'.")

if __name__ == "__main__":
    main()

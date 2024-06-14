import pandas as pd
from bs4 import BeautifulSoup
import re
from fuzzywuzzy import fuzz

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
    # Rimuove solo i suffissi di ambiente noti
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

def extract_runtime_versions_from_html(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        runtime_versions = {}

        # Trova tutti i div con la classe 'public_fixedDataTableCell_cellContent'
        divs = soup.find_all('div', class_='public_fixedDataTableCell_cellContent')
        
        for div in divs:
            # Trova tutti i tag <span> all'interno del div corrente
            spans = div.find_all('span', {'data-testid': re.compile(r'.*-runtime-version-base-version$')})
            
            for span in spans:
                # Estrai il nome dell'applicazione dal data-testid
                app_name = span['data-testid'].split('-runtime-version-base-version')[0]
                # Estrai il contenuto del tag span
                version = span.text.strip()
                # Aggiungi alla lista delle versioni di runtime
                runtime_versions[app_name] = version

        return runtime_versions if runtime_versions else None

    except Exception as e:
        print(f"Errore durante l'estrazione delle versioni di runtime dall'HTML: {e}")
        return None

def generate_report_file(output_file_path, project_name, project_apps, discrepancies, runtime_versions_html):
    try:
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(f"Rapporto di controllo per il progetto '{project_name if project_name else 'Non specificato'}'\n")
            file.write("\nNomi delle applicazioni:\n")
            for name in project_apps:
                file.write(f"{name}\n")
            
            file.write("\nDiscrepanze nelle versioni di runtime tra HTML e Excel:\n")
            if discrepancies:
                for name in discrepancies:
                    file.write(f"{name}\n")
            else:
                file.write("Nessuna discrepanza trovata.\n")
            
            file.write("\nVersione di runtime dall'HTML:\n")
            for app_name, version in runtime_versions_html.items():
                file.write(f"{app_name}: {version}\n")
    except Exception as e:
        print(f"Errore durante la scrittura del file di report: {e}")

def find_best_match(name, names_list):
    best_match = None
    max_similarity = -1
    
    for candidate in names_list:
        similarity = fuzz.ratio(name, candidate)
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = candidate
            
    return best_match

def main():
    html_file_path = r'C:\Users\kevin\Documents\Automatizzazioni\FSTR_PROD.html'
    excel_file_path = r'C:\Users\kevin\Documents\Automatizzazioni\FSTR.xlsx'
    output_file_path = r'C:\Users\kevin\Documents\Automatizzazioni\SupportScopeReport.txt'

    website_content = read_html_content(html_file_path)
    if website_content is None:
        return

    runtime_versions_html = extract_runtime_versions_from_html(website_content)
    if not runtime_versions_html:
        print("Versioni di runtime non trovate nell'HTML. Impossibile procedere con il confronto.")
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

        filtered_df = df[df[project_column].astype(str).str.lower() == project_name.lower()]
        project_apps = {name.strip().lower() for name in filtered_df['APIs Name'].dropna()}
    else:
        project_apps = {name.strip().lower() for name in df['APIs Name'].dropna()}

    print(f"Nomi delle applicazioni per il progetto '{project_name if project_name else 'Non specificato'}':")
    for name in project_apps:
        print(name)

    discrepancies = set()
    for app_name in project_apps:
        # Verifica se il nome dell'applicazione è presente nelle versioni di runtime estratte dall'HTML
        best_match_html = find_best_match(app_name, runtime_versions_html.keys())
        
        if best_match_html is not None:
            try:
                runtime_version_excel = df.loc[df['APIs Name'].str.lower() == app_name]['Runtime Version'].iloc[0]
                runtime_version_html = runtime_versions_html[best_match_html]

                if runtime_version_html.strip() != runtime_version_excel.strip():
                    discrepancies.add(app_name)
            except KeyError:
                print(f"Colonna 'Runtime Version' non trovata nel dataframe per l'applicazione '{app_name}'.")
        else:
            print(f"Versione di runtime non trovata per '{app_name}' nell'HTML.")

    if discrepancies:
        print(f"\nDiscrepanze nelle versioni di runtime tra HTML e Excel per il progetto '{project_name if project_name else 'Non specificato'}':")
        for name in discrepancies:
            print(name)
    else:
        print(f"\nNessuna discrepanza nelle versioni di runtime tra HTML e Excel per il progetto '{project_name if project_name else 'Non specificato'}'.")

    generate_report_file(output_file_path, project_name, project_apps, discrepancies, runtime_versions_html)

if __name__ == "__main__":
    main()

import pandas as pd
from bs4 import BeautifulSoup

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
    return name.strip().lower()

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

def main():
    html_file_path = r'C:\Users\kevin\Documents\Automatizzazioni\Tiffany.html'
    excel_file_path = r'C:\Users\kevin\Documents\Automatizzazioni\Tiffany.xlsx'

    website_content = read_html_content(html_file_path)
    if website_content is None:
        return

    soup = BeautifulSoup(website_content, 'html.parser')
    classToFind = soup.find_all('a', class_='sc-csuQGl fgtqry')
    html_texts = {normalize_name(tag.get_text()) for tag in classToFind}

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
        project_apps = {normalize_name(name) for name in filtered_df['APIs Name'].str.strip()}
    else:
        project_apps = {normalize_name(name) for name in df['APIs Name'].str.strip()}

    html_not_in_excel = html_texts.difference(project_apps)
    excel_not_in_html = project_apps.difference(html_texts)
    unique_names = html_not_in_excel.union(excel_not_in_html)

    if unique_names:
        print(f"Applicazioni mancanti per il progetto '{project_name if project_name else ''}':")
        for name in unique_names:
            print(name)
    else:
        print(f"Nessuna applicazione mancante per il progetto '{project_name if project_name else ''}'.")

if __name__ == "__main__":
    main()

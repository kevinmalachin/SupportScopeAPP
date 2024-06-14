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

def extract_applications_from_html(html_content, class_name):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        applications = set()

        # Trova tutti gli elementi con la classe specificata
        elements = soup.find_all(class_=class_name)

        for element in elements:
            # Estrai il testo e aggiungi alla lista delle applicazioni
            app_name = element.text.strip().lower()
            applications.add(app_name)

        return applications if applications else None

    except Exception as e:
        print(f"Errore durante l'estrazione delle applicazioni dall'HTML: {e}")
        return None

def read_excel_file(file_path):
    try:
        engines = ['openpyxl', 'xlrd', 'odf', 'pyxlsb']
        for engine in engines:
            try:
                return pd.read_excel(file_path, sheet_name='APIs Scope', engine=engine)
            except Exception as e:
                print(f"Errore con il motore {engine}: {e}")
        return None
    except Exception as e:
        print(f"Errore durante la lettura del file Excel: {e}")
        return None

def find_discrepancies(excel_apps, html_apps):
    try:
        # Trova le applicazioni presenti solo nell'HTML
        html_only = html_apps - excel_apps
        # Trova le applicazioni presenti solo nell'Excel
        excel_only = excel_apps - html_apps

        return html_only, excel_only

    except Exception as e:
        print(f"Errore durante la ricerca delle discrepanze: {e}")
        return None, None

def generate_report(output_file_path, project_name, excel_apps, html_only, excel_only):
    try:
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(f"Rapporto di controllo per il progetto '{project_name if project_name else 'Non specificato'}'\n\n")
            file.write("Nomi delle applicazioni:\n")
            for name in sorted(excel_apps):
                file.write(f"{name}\n")

            file.write("\nDiscrepanze tra HTML ed Excel:\n")
            file.write("Applicazioni trovate solo nell'HTML:\n")
            for name in sorted(html_only):
                file.write(f"{name}\n")

            file.write("\nApplicazioni trovate solo nell'Excel:\n")
            for name in sorted(excel_only):
                file.write(f"{name}\n")

        print(f"Rapporto generato con successo: {output_file_path}")

    except Exception as e:
        print(f"Errore durante la generazione del rapporto: {e}")

def main():
    try:
        html_file_path = r'C:\Users\kevin\Documents\Automatizzazioni\FSTR_PROD.html'
        excel_file_path = r'C:\Users\kevin\Documents\Automatizzazioni\FSTR.xlsx'
        output_file_path = r'C:\Users\kevin\Desktop\OutputScope\SupportScopeReport.txt'
        class_name = 'sc-csuQGl fgtqry'  # Classe HTML corretta per i nomi delle applicazioni

        website_content = read_html_content(html_file_path)
        if website_content is None:
            return

        html_apps = extract_applications_from_html(website_content, class_name)
        if html_apps is None:
            print("Applicazioni non trovate nell'HTML. Impossibile procedere con il confronto.")
            return

        df = read_excel_file(excel_file_path)
        if df is None:
            print(f"Errore durante la lettura del file Excel: {excel_file_path}")
            return

        excel_apps = set(df['APIs Name'].dropna().str.strip().str.lower())

        html_only, excel_only = find_discrepancies(excel_apps, html_apps)

        project_name = input("Inserisci il nome del progetto (es. KAM) o premi invio per saltare il controllo: ").strip()

        generate_report(output_file_path, project_name, excel_apps, html_only, excel_only)

    except Exception as e:
        print(f"Errore durante l'esecuzione del programma: {e}")

if __name__ == "__main__":
    main()

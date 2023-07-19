from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


class Insolvency_Checker:
    def __init__(self):

        s=Service(ChromeDriverManager().install())
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=s, options=options)
        self.wait = WebDriverWait(self.driver, 1)

        url = 'https://neu.insolvenzbekanntmachungen.de/ap/suche.jsf'  # Replace with the URL of your form
        self.driver.get(url)


    def submit_form(self, date_from: str, date_to: str, query: str, city: str=''):
        
        self.driver.find_element(By.NAME, "frm_suche:ldi_datumVon:datumHtml5").send_keys(date_from)
        self.driver.find_element(By.NAME, "frm_suche:ldi_datumBis:datumHtml5").send_keys(date_to)
        self.driver.find_element(By.NAME, "frm_suche:litx_firmaNachName:text").send_keys(query)
        self.driver.find_element(By.NAME, "frm_suche:litx_sitzWohnsitz:text").send_keys(city)

        
        submit_button = self.driver.find_element(By.NAME, "frm_suche:cbt_suchen")
        self.driver.execute_script("arguments[0].scrollIntoView();", submit_button)

        self.wait.until(EC.element_to_be_clickable((By.NAME, "frm_suche:cbt_suchen")))

        self.driver.execute_script("arguments[0].click();", submit_button)

        page_source = self.driver.page_source

        self.driver.quit()
        
        results = self.extract_table_data(page_source)
        return results


    def extract_table_data(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        table = soup.find('table', {'id': 'tbl_ergebnis'})

        if table is None:
            return None

        tbody = table.find('tbody')

        if tbody is None:
            return None

        rows = tbody.find_all('tr')

        data = []
        for row in rows:
            cols = row.find_all('td')
            row_data = {
                "Veröffent­lichungsdatum": cols[0].text.strip(),
                "aktuelles Aktenzeichen": cols[1].text.strip(),
                "Gericht": cols[2].text.strip(),
                "Name, Vorname / Bezeichnung": cols[3].text.strip(),
                "Sitz / Wohnsitz": cols[4].text.strip(),
                "Register": cols[5].text.strip()
            }
            data.append(row_data)

        return data

if __name__ == '__main__':
    checker = Insolvency_Checker()
    data = checker.submit_form('01.01.2010', '30.06.2023', '*Air Berlin*')
    print(data)

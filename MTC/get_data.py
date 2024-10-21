# fetch("https://she.mtc.gob.pe/ieqhomgestionar/index", {
#   "headers": {
#     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#     "accept-language": "es,en;q=0.9,en-US;q=0.8",
#     "cache-control": "no-cache",
#     "content-type": "application/x-www-form-urlencoded",
#     "pragma": "no-cache",
#     "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Opera\";v=\"114\"",
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": "\"Windows\"",
#     "sec-fetch-dest": "document",
#     "sec-fetch-mode": "navigate",
#     "sec-fetch-site": "same-origin",
#     "sec-fetch-user": "?1",
#     "upgrade-insecure-requests": "1"
#   },
#   "referrer": "https://she.mtc.gob.pe/ieqhomgestionar/index",
#   "referrerPolicy": "strict-origin-when-cross-origin",
#   "body": "NumeroCertificado=&Marca=&Modelo=&Empresa=tenda&hdPag=8&hdTotal=74&hdRegxPag=10",
#   "method": "POST",
#   "mode": "cors",
#   "credentials": "include"
# });

import requests, pandas as pd
from bs4 import BeautifulSoup
from environ import url
import re, math
from io import StringIO
from tqdm import tqdm


class TelMTC:
    def __init__(self, num_cert="", marca="", model="", empresa=""):

        self.params = {
            # "NumeroCertificado": num_cert,
            "Marca": marca,
            # "Modelo": model,
            # "Empresa": empresa,
        }
        self.first_page()

    def post_data(self):
        response = requests.post(url, data=self.params)
        return response

    def first_page(self, total_n_by_page=10):
        # primera pagina
        response = self.post_data()
        self.first_page_response = response
        # total_registros
        soup = self.to_soup(response.content)
        total_registros = soup.find("span", class_="total-registros").get_text()
        resultado = re.search(r"\d+", total_registros)
        numero = int(resultado.group())
        total_pages = math.ceil(numero / total_n_by_page)
        self.total_pages = total_pages

    def update_params(self, n_page):
        self.params["hdPag"] = n_page
        response_n = self.post_data()
        return response_n

    @staticmethod
    def to_soup(content_html):
        soup = BeautifulSoup(content_html, features="html.parser")
        return soup

    @staticmethod
    def html_to_pandas(html) -> pd.DataFrame:
        table_data = html.find("table", class_="table")
        data = pd.read_html(StringIO(str(table_data)))[0]
        return data

    def get_data(self):
        content_html = self.first_page_response.content
        total_pages = self.total_pages
        html = self.to_soup(content_html)
        data_fp = self.html_to_pandas(html)
        data = [data_fp]
        for page in tqdm(range(2, total_pages + 1)):
            response_n = self.update_params(page)
            html_n = self.to_soup(response_n.content)
            data.append(self.html_to_pandas(html_n))
        return pd.concat(data, ignore_index=True)


data = TelMTC(marca="samsung").get_data()

print(data)

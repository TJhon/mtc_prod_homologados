
import requests, pandas as pd
from bs4 import BeautifulSoup
from environ import url
import re, math
from io import StringIO
from tqdm import tqdm


NEW_NAMES = [
    "n",
    "type",
    "cert",
    "brand",
    "model",
    "manufacturer",
    "function",
    "date",
    "nan",
]


class TelMTC:
    def __init__(self, num_cert="", marca="", model="", empresa=""):

        self.params = {
            "NumeroCertificado": num_cert,
            "Marca": marca,
            "Modelo": model,
            "Empresa": empresa,
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

    def fetch_data(self):
        content_html = self.first_page_response.content
        total_pages = self.total_pages
        html = self.to_soup(content_html)
        data_fp = self.html_to_pandas(html)
        data = [data_fp]
        for page in tqdm(range(2, total_pages + 1)):
            response_n = self.update_params(page)
            html_n = self.to_soup(response_n.content)
            data.append(self.html_to_pandas(html_n))

        data_final = pd.concat(data, ignore_index=True)
        data_final.columns = NEW_NAMES
        data_final.drop(columns=["n", "nan"], inplace=True)
        # por el momento todo sera usando la marca 
        data_final['tipo_busqueda'] = 'marca'
        data_final['termino_busqueda'] = self.params['Marca']
        return data_final



def agregar_columnas(df: pd.DataFrame, args) -> pd.DataFrame:
    """
    Agrega las columnas requeridas al DataFrame:
    - termino_busqueda
    - valor_busqueda
    - nombre_comercial (por defecto None)
    """
    termino = ""
    valor = ""

    if args.num_cert:
        termino = "num_cert"
        valor = args.num_cert
    elif args.marca:
        termino = "marca"
        valor = args.marca
    elif args.model:
        termino = "model"
        valor = args.model
    elif args.empresa:
        termino = "empresa"
        valor = args.empresa

    df["termino_busqueda"] = termino
    df["valor_busqueda"] = valor
    df["nombre_comercial"] = None  # será NULL en SQL

    return df



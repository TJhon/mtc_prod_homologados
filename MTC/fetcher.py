
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
        return data_final
    
        # # tqdm.pandas()
        # # d = data_final = data_final.head(5)
        # comercial_name = {}
        # comercial_name_list = []
        # querys = []

        # def fetch_commercial_name(row):
        #     brand, model = row["brand"], row["model"]
        #     query = brand + model
        #     if query in comercial_name:
        #         return comercial_name[query]

        #     comercial_name_search = SearchEngine(brand, model).run()
        #     comercial_name[query] = comercial_name_search
        #     return comercial_name_search

        # # Procesamiento paralelo no disponible por pasar el limite de peticiones

        # # Alternativa solo buscar si no existe los datos para ese modelo y marca
        # for index, row in tqdm(data_final.iterrows(), total=data_final.shape[0]):
        #     brand, model = row["brand"], row["model"]
        #     query = brand + model
        #     # print(query)
        #     if query in querys:
        #         comercial_name_list.append(comercial_name[query])
        #         continue

        #     querys.append(query)

        #     comercial_name_search = SearchEngine(brand, model).run()
        #     comercial_name[query] = comercial_name_search
        #     comercial_name_list.append(comercial_name_search)

        # data_final["commercial_name"] = comercial_name_list

        # return data_final



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

def save_prostgres(df):
    from dotenv import load_dotenv
    import os
    from sqlalchemy import create_engine

    load_dotenv()
    PG_USER = os.getenv("PG_USER")
    PG_PASSWORD = os.getenv("PG_PASSWORD")
    PG_HOST = os.getenv("PG_HOST")
    PG_PORT = os.getenv("PG_PORT")
    PG_DB = os.getenv("PG_DB")

    values = [PG_USER, PG_PASSWORD, PG_HOST, PG_PORT, PG_DB]
    # print(values)
    if not all(values):
        raise ValueError("❌ Faltan variables requeridas en el archivo .env")

    urlpg = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    engine = create_engine(urlpg)

    df.to_sql(
        "productos_mtc",
        engine,
        if_exists="append",
        index=False,
    ) 


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Fetcher de productos homologados del MTC")

    parser.add_argument("--num_cert", default="", help="Número de certificado")
    parser.add_argument("--marca", default="por_defecto", help="Marca del equipo")
    parser.add_argument("--model", default="", help="Modelo del equipo")
    parser.add_argument("--empresa", default="", help="Empresa")
    parser.add_argument("--save", action="store_true", help="Guardar en PostgreSQL")

    args = parser.parse_args()

    data: pd.DataFrame = TelMTC(
        num_cert=args.num_cert,
        marca=args.marca,
        model=args.model,
        empresa=args.empresa,
    ).fetch_data()

    data = agregar_columnas(data, args)

    if args.save:
        save_prostgres(data)
    # print(tel)

    # data = TelMTC(marca="", num_cert="TRFM48192").fetch_data()
    # print(data)

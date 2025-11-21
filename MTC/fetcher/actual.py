import pandas as pd, os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine

def fetch_actual_data(search_method = 'marca', search_value:str = None):
    load_dotenv(find_dotenv())
    search_value = search_value.lower().strip()

    PG_USER = os.getenv("PG_USER")
    PG_PASSWORD = os.getenv("PG_PASSWORD")
    PG_HOST = os.getenv("PG_HOST")
    PG_PORT = os.getenv("PG_PORT")
    PG_DB = os.getenv("PG_DB")

    values = [PG_USER, PG_PASSWORD, PG_HOST, PG_PORT, PG_DB]
    if not all(values):
        raise ValueError("❌ Faltan variables requeridas en el archivo .env")

    urlpg = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    engine = create_engine(urlpg)
    actual_data = pd.read_sql(
        f"""select * from productos_mtc
        where termino_busqueda = '{search_method}' and valor_busqueda= '{search_value}'
        """
        , con = engine
    )

    return actual_data

# hay duplicados por marcca/modelo pero no por  certificodo, por lo que un modelo puede tener 1 o mas certificados de homologacion

if __name__ == "__main__":
    print(fetch_actual_data(search_value='Poco'))


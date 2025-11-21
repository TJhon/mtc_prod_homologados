def pg_upload_to_supabase(df):
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
    return df

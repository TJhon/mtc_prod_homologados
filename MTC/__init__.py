
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

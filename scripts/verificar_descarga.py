"""Compara data/raw con los archivos que publica la TLC y revisa que DuckDB pueda leerlos"""

import argparse
import csv
import re

import duckdb
import requests

# Años, tipos y rutas salen del script de descarga para que los dos usen la misma lista
from download_data import ANIOS, DIR_DESTINO, TIPOS_TAXI, URL_BASE

PAGINA = "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page"
RAIZ = DIR_DESTINO.parents[1]
SALIDA = RAIZ / "docs" / "evidencias" / "02_verificacion_descarga.csv"
CAMPOS = ["tipo", "archivo", "bytes_servidor", "bytes_local", "registros", "estado"]


def publicados(anios):
    # Archivos enlazados en la página oficial, una fuente distinta del script de descarga
    html = requests.get(PAGINA, headers={"User-Agent": "Mozilla/5.0"}, timeout=60).text
    patron = rf"({'|'.join(TIPOS_TAXI)})_tripdata_({'|'.join(map(str, anios))})-(\d\d)\.parquet"
    return sorted(set(re.findall(patron, html)))


def revisar(tipo, anio, mes):
    nombre = f"{tipo}_tripdata_{anio}-{mes}.parquet"
    ruta = DIR_DESTINO / tipo / anio / nombre
    servidor = int(requests.head(f"{URL_BASE}/{nombre}", timeout=60).headers["Content-Length"])
    fila = {"tipo": tipo, "archivo": nombre, "bytes_servidor": servidor, "bytes_local": None, "registros": None}
    if not ruta.exists():
        return fila | {"estado": "falta"}
    fila["bytes_local"] = ruta.stat().st_size
    if fila["bytes_local"] != servidor:
        return fila | {"estado": "tamaño distinto"}
    try:
        consulta = f"SELECT num_rows FROM parquet_file_metadata('{ruta.as_posix()}')"
        fila["registros"] = duckdb.sql(consulta).fetchone()[0]
    except duckdb.Error:
        return fila | {"estado": "no se puede leer"}
    return fila | {"estado": "completo"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anios", type=int, nargs="+", default=list(ANIOS))
    args = parser.parse_args()

    esperados = publicados(args.anios)
    filas = [revisar(*archivo) for archivo in esperados]

    nombres = {f["archivo"] for f in filas}
    for anio in args.anios:
        for ruta in sorted(DIR_DESTINO.glob(f"*/{anio}/*.parquet")):
            if ruta.name not in nombres:
                filas.append({"tipo": ruta.parent.parent.name, "archivo": ruta.name, "bytes_servidor": None,
                              "bytes_local": ruta.stat().st_size, "registros": None, "estado": "no publicado"})

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(SALIDA, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(filas)

    for f in filas:
        print(f"{f['archivo']}: {f['estado']}, {f['registros']} registros")
    completos = sum(f["estado"] == "completo" for f in filas)
    print(f"{completos} de {len(esperados)} archivos publicados completos. Detalle en {SALIDA.relative_to(RAIZ).as_posix()}")
    if completos != len(filas):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

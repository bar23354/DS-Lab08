"""Muestra las herramientas del ambiente, prueba DuckDB sobre un Parquet y revisa que Metabase responda"""

import platform
import tempfile
from importlib.metadata import version
from pathlib import Path

import duckdb
import requests

RAIZ = Path(__file__).resolve().parents[1]
PAQUETES = ["duckdb", "pandas", "pyarrow", "matplotlib", "requests", "jupyterlab"]
CARPETAS = ["data/raw", "data/processed", "notebooks", "scripts", "sql", "docs"]
METABASE = "http://metabase:3000/api/health"


def main():
    print(f"Python {platform.python_version()} en {platform.system()}")
    for paquete in PAQUETES:
        print(f"{paquete} {version(paquete)}")

    with tempfile.TemporaryDirectory() as tmp:
        ruta = (Path(tmp) / "prueba.parquet").as_posix()
        duckdb.sql(f"COPY (SELECT range AS id FROM range(1000)) TO '{ruta}' (FORMAT parquet)")
        filas = duckdb.sql(f"SELECT count(*) FROM '{ruta}'").fetchone()[0]
    print(f"DuckDB escribe y lee Parquet: {filas} filas")

    faltan = [c for c in CARPETAS if not (RAIZ / c).is_dir()]
    print("Estructura completa" if not faltan else f"Faltan carpetas: {faltan}")

    # Dentro de Compose el servicio metabase se encuentra por su nombre
    try:
        estado = requests.get(METABASE, timeout=10).json().get("status")
    except requests.RequestException:
        estado = "sin respuesta"
    print(f"Metabase: {estado}")


if __name__ == "__main__":
    main()

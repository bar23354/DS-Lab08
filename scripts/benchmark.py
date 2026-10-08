"""Compara las mismas consultas sobre los Parquet y sobre una tabla de DuckDB con tres cantidades de datos"""

import csv
import os
import statistics
import time
from pathlib import Path

import duckdb

RAIZ = Path(__file__).resolve().parents[1]
SQL = RAIZ / "sql"
RAW = RAIZ / "data" / "raw"
PROCESADOS = RAIZ / "data" / "processed"
EVIDENCIAS = RAIZ / "docs" / "evidencias"
REPETICIONES = 5

# Archivos de cada conjunto, como patrón dentro de data/raw/<tipo>/
CONJUNTOS = {
    "1 mes": "2026/*_2026-01.parquet",
    "8 meses": "2026/*.parquet",
    "20 meses": "202[46]/*.parquet",
}
CONSULTAS = [
    "benchmark/01_conteo.sql",
    "benchmark/02_un_dia.sql",
    "benchmark/03_percentiles_total.sql",
    "ej4/01_viajes_por_mes.sql",
    "ej4/02_viajes_por_hora.sql",
    "ej4/06_distritos.sql",
    "ej4/09_formas_de_pago.sql",
]


def vistas(patron):
    # Las mismas vistas del análisis, limitadas a los archivos del conjunto
    texto = (SQL / "vistas.sql").read_text(encoding="utf-8")
    return texto.replace("/*/*.parquet'", f"/{patron}'")


def materializar(ruta, patron):
    ruta.unlink(missing_ok=True)
    con = duckdb.connect(str(ruta))
    con.execute(vistas(patron))
    inicio = time.perf_counter()
    con.execute("CREATE TABLE viajes_tabla AS SELECT * FROM viajes")
    con.execute("CREATE TABLE zonas_tabla AS SELECT * FROM zonas")
    segundos = time.perf_counter() - inicio
    # viajes_validos queda igual y pasa a leer la tabla
    con.execute("CREATE OR REPLACE VIEW viajes AS SELECT * FROM viajes_tabla")
    con.execute("CREATE OR REPLACE VIEW zonas AS SELECT * FROM zonas_tabla")
    registros = con.execute("SELECT count(*) FROM viajes_tabla").fetchone()[0]
    con.close()
    return segundos, registros


def medir(con, texto):
    # Una ejecución inicial y REPETICIONES más, de las que se reportan mediana, mínimo y máximo
    tiempos = []
    for _ in range(REPETICIONES + 1):
        inicio = time.perf_counter()
        resultado = con.execute(texto).fetchall()
        tiempos.append(time.perf_counter() - inicio)
    resto = tiempos[1:]
    return resultado, {
        "primera_s": round(tiempos[0], 4),
        "mediana_s": round(statistics.median(resto), 4),
        "minimo_s": round(min(resto), 4),
        "maximo_s": round(max(resto), 4),
    }


def iguales(a, b):
    if len(a) != len(b):
        return False
    for fila_a, fila_b in zip(sorted(a, key=str), sorted(b, key=str)):
        for x, y in zip(fila_a, fila_b):
            if isinstance(x, float) and isinstance(y, float):
                if abs(x - y) > 0.01:
                    return False
            elif x != y:
                return False
    return True


def guardar(nombre, filas):
    with open(EVIDENCIAS / nombre, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=filas[0].keys())
        escritor.writeheader()
        escritor.writerows(filas)


def main():
    os.chdir(RAIZ)
    PROCESADOS.mkdir(parents=True, exist_ok=True)
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    tablas, tiempos = [], []

    for conjunto, patron in CONJUNTOS.items():
        archivos = list(RAW.glob(f"*/{patron}"))
        ruta = PROCESADOS / f"benchmark_{conjunto.replace(' ', '_')}.duckdb"
        segundos, registros = materializar(ruta, patron)
        tablas.append({
            "conjunto": conjunto,
            "archivos": len(archivos),
            "registros": registros,
            "mb_parquet": round(sum(a.stat().st_size for a in archivos) / 1e6, 1),
            "mb_duckdb": round(ruta.stat().st_size / 1e6, 1),
            "creacion_tabla_s": round(segundos, 2),
        })
        print(f"{conjunto}: {registros:,} registros, tabla creada en {segundos:.1f} s")

        # Una estrategia a la vez, para que no compitan por memoria
        resultados, filas = {}, []
        for estrategia in ["parquet", "tabla"]:
            if estrategia == "parquet":
                con = duckdb.connect()
                con.execute(vistas(patron))
            else:
                con = duckdb.connect(str(ruta), read_only=True)
            for consulta in CONSULTAS:
                resultado, medidas = medir(con, (SQL / consulta).read_text(encoding="utf-8"))
                resultados[consulta, estrategia] = resultado
                filas.append({"conjunto": conjunto, "registros": registros, "consulta": consulta,
                              "estrategia": estrategia, **medidas})
            con.close()

        for fila in filas:
            fila["mismo_resultado"] = iguales(resultados[fila["consulta"], "parquet"], resultados[fila["consulta"], "tabla"])
            print(f"  {fila['consulta']} {fila['estrategia']}: {fila['mediana_s']:.3f} s, mismo resultado {fila['mismo_resultado']}")
        tiempos.extend(filas)

    guardar("06_benchmark_tablas.csv", tablas)
    guardar("06_benchmark_tiempos.csv", tiempos)
    print("Resultados en docs/evidencias/06_benchmark_tablas.csv y docs/evidencias/06_benchmark_tiempos.csv")


if __name__ == "__main__":
    main()

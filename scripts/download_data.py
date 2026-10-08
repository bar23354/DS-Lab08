#!/usr/bin/env python3
"""Descarga los archivos Parquet de taxis amarillos y verdes del NYC TLC Trip Record Data

Fuente oficial de los datos:
    https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Uso:
    python scripts/download_data.py                   # amarillos y verdes de los años de ANIOS
    python scripts/download_data.py --taxi yellow
    python scripts/download_data.py --anios 2025 2026

Los archivos se guardan en data/raw/<tipo>/<anio>/<nombre-original>.parquet

Comportamiento:
  - Pregunta al servidor qué meses están publicados y distingue un mes sin publicar de un error de red
  - Un archivo que ya existe y es un Parquet completo no se vuelve a descargar
  - Descarga sobre un nombre temporal, compara los bytes con el tamaño del servidor y recién entonces renombra
"""

import argparse
import sys
from pathlib import Path

import requests

ANIOS = (2026,)
TIPOS_TAXI = ("yellow", "green")
URL_BASE = "https://d37ci6vzurychx.cloudfront.net/trip-data"
# Ruta calculada desde la ubicación del script, así no depende de la carpeta de trabajo
DIR_DESTINO = Path(__file__).resolve().parents[1] / "data" / "raw"

TIEMPO_ESPERA = 60          # segundos por petición
INTENTOS = 3                # intentos por archivo antes de darse por vencido
BLOQUE = 1024 * 1024        # 1 MiB por bloque de descarga
SUFIJO_TEMPORAL = ".part"
MARCA_PARQUET = b"PAR1"     # bytes con los que empieza y termina todo Parquet


def construir_nombre(tipo: str, anio: int, mes: int) -> str:
    """Nombre del archivo publicado por la TLC, p. ej. yellow_tripdata_2026-01.parquet"""
    return f"{tipo}_tripdata_{anio}-{mes:02d}.parquet"


def construir_url(tipo: str, anio: int, mes: int) -> str:
    """URL completa del archivo Parquet mensual"""
    return f"{URL_BASE}/{construir_nombre(tipo, anio, mes)}"


def ruta_destino(tipo: str, anio: int, mes: int) -> Path:
    """Ruta local donde se guarda el archivo"""
    return DIR_DESTINO / tipo / str(anio) / construir_nombre(tipo, anio, mes)


def es_parquet_completo(ruta: Path) -> bool:
    """Revisa la marca PAR1 al inicio y al final, que falta en un archivo cortado o en una página de error"""
    if not ruta.exists() or ruta.stat().st_size < 2 * len(MARCA_PARQUET):
        return False
    with ruta.open("rb") as archivo:
        inicio = archivo.read(len(MARCA_PARQUET))
        archivo.seek(-len(MARCA_PARQUET), 2)
        fin = archivo.read(len(MARCA_PARQUET))
    return inicio == MARCA_PARQUET and fin == MARCA_PARQUET


def tamanio_publicado(url: str) -> int | None:
    """Tamaño del archivo en el servidor, o None si la TLC aún no lo publica

    Un error de red se propaga para que no se confunda con un mes sin publicar
    """
    respuesta = requests.head(url, timeout=TIEMPO_ESPERA, allow_redirects=True)
    if respuesta.status_code in (403, 404):
        return None
    respuesta.raise_for_status()
    return int(respuesta.headers.get("Content-Length", 0))


def formato_tamanio(n: float) -> str:
    for unidad in ("B", "KiB", "MiB", "GiB"):
        if n < 1024 or unidad == "GiB":
            return f"{n:.1f} {unidad}"
        n /= 1024
    return f"{n:.1f} GiB"


def descargar_archivo(url: str, destino: Path, esperado: int) -> int:
    """Descarga url en destino y devuelve los bytes escritos, que deben coincidir con esperado"""
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_name(destino.name + SUFIJO_TEMPORAL)

    ultimo_error = None
    for intento in range(1, INTENTOS + 1):
        try:
            with requests.get(url, stream=True, timeout=TIEMPO_ESPERA) as respuesta:
                respuesta.raise_for_status()
                escritos = 0
                with temporal.open("wb") as archivo:
                    for bloque in respuesta.iter_content(chunk_size=BLOQUE):
                        if bloque:
                            archivo.write(bloque)
                            escritos += len(bloque)
            if escritos == 0 or (esperado and escritos != esperado):
                raise requests.RequestException(f"llegaron {escritos} de {esperado} bytes")
            temporal.replace(destino)
            return escritos
        except requests.RequestException as error:
            ultimo_error = error
            temporal.unlink(missing_ok=True)
            if intento < INTENTOS:
                print(f"      intento {intento}/{INTENTOS} fallido ({error}), se reintenta")

    raise requests.RequestException(f"no se pudo descargar {url}: {ultimo_error}")


def descargar(tipo: str, anio: int) -> dict:
    """Descarga todos los meses publicados de un tipo de taxi y un año"""
    print(f"\n=== {tipo.upper()} {anio} ===")
    resumen = {"descargados": 0, "omitidos": 0, "no_publicados": [], "fallidos": []}

    for mes in range(1, 13):
        etiqueta = f"{anio}-{mes:02d}"
        destino = ruta_destino(tipo, anio, mes)

        if es_parquet_completo(destino):
            print(f"  {etiqueta}  ya existe, se omite")
            resumen["omitidos"] += 1
            continue
        if destino.exists():
            print(f"  {etiqueta}  el archivo local está incompleto, se descarga de nuevo")

        url = construir_url(tipo, anio, mes)
        try:
            esperado = tamanio_publicado(url)
            if esperado is None:
                print(f"  {etiqueta}  aun no publicado por la TLC")
                resumen["no_publicados"].append(etiqueta)
                continue
            print(f"  {etiqueta}  descargando...")
            escritos = descargar_archivo(url, destino, esperado)
        except requests.RequestException as error:
            print(f"  {etiqueta}  ERROR: {error}")
            resumen["fallidos"].append(etiqueta)
        else:
            print(f"  {etiqueta}  listo ({formato_tamanio(escritos)}) en {destino.relative_to(DIR_DESTINO.parents[1])}")
            resumen["descargados"] += 1

    return resumen


def main() -> int:
    parser = argparse.ArgumentParser(description="Descarga los datos de taxis del NYC TLC")
    parser.add_argument(
        "--taxi", choices=(*TIPOS_TAXI, "all"), default="all",
        help="tipo de taxi a descargar (por defecto: all)",
    )
    parser.add_argument(
        "--anios", type=int, nargs="+", default=list(ANIOS),
        help=f"años a descargar (por defecto: {' '.join(map(str, ANIOS))})",
    )
    argumentos = parser.parse_args()

    tipos = TIPOS_TAXI if argumentos.taxi == "all" else (argumentos.taxi,)

    total = {"descargados": 0, "omitidos": 0, "no_publicados": [], "fallidos": []}
    for tipo in tipos:
        for anio in argumentos.anios:
            resumen = descargar(tipo, anio)
            total["descargados"] += resumen["descargados"]
            total["omitidos"] += resumen["omitidos"]
            total["no_publicados"] += [f"{tipo} {m}" for m in resumen["no_publicados"]]
            total["fallidos"] += [f"{tipo} {m}" for m in resumen["fallidos"]]

    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"  descargados   : {total['descargados']}")
    print(f"  ya existian   : {total['omitidos']}")
    print(f"  no publicados : {len(total['no_publicados'])}")
    if total["no_publicados"]:
        print(f"      {', '.join(total['no_publicados'])}")
    print(f"  fallidos      : {len(total['fallidos'])}")
    if total["fallidos"]:
        print(f"      {', '.join(total['fallidos'])}")
    print("=" * 60)

    return 1 if total["fallidos"] else 0


if __name__ == "__main__":
    sys.exit(main())

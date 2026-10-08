"""Calcula los indicadores en una base de DuckDB y arma el tablero en Metabase

Se ejecuta dentro del servicio lab:
    python scripts/tablero_metabase.py

Pasos:
  1. Ejecuta cada consulta de sql/indicadores sobre los Parquet y guarda el resultado como tabla en
     data/processed/tablero.duckdb, que Metabase abre sin permiso de escritura
  2. Crea o reutiliza el usuario administrador de Metabase, la conexión a DuckDB, una pregunta por
     indicador y el tablero con un filtro por tipo de taxi

Las credenciales salen de MB_EMAIL y MB_PASSWORD, con valores por defecto para la instancia local
"""

import os
import time
import uuid
from pathlib import Path

import duckdb
import requests

RAIZ = Path(__file__).resolve().parents[1]
SQL = RAIZ / "sql"
BASE = RAIZ / "data" / "processed" / "tablero.duckdb"
# Ruta de la base dentro del contenedor de Metabase, que monta data en /workspace/data
BASE_METABASE = "/workspace/data/processed/tablero.duckdb"
METABASE = os.environ.get("MB_URL", "http://metabase:3000")
EMAIL = os.environ.get("MB_EMAIL", "lab8@uvg.edu.gt")
CLAVE = os.environ.get("MB_PASSWORD", "lab8-duckdb-2026")
NOMBRE_BASE = "Taxis de Nueva York (DuckDB)"
NOMBRE_TABLERO = "Viajes de taxi en Nueva York"

INDICADORES = [
    {
        "tabla": "i1_viajes_por_dia", "sql": "01_viajes_por_dia.sql", "titulo": "I1 Viajes por día",
        "pregunta": "¿Cuántos viajes hay por día y cómo cambia entre meses y años?", "unidad": "Viajes por día",
        "interpretacion": "De enero a agosto, los viajes amarillos por día subieron 13% en 2025 y bajaron 1.6% en 2026. "
                          "Los verdes bajan cada año, 22% entre 2024 y 2026. En los tres años la demanda cae en julio y agosto.",
    },
    {
        "tabla": "i2_total_mediano", "sql": "02_total_mediano.sql", "titulo": "I2 Total del viaje mediano",
        "pregunta": "¿Cuánto paga un pasajero en un viaje típico?", "unidad": "Dólares",
        "interpretacion": "De enero a agosto, el viaje amarillo mediano pasó de 21.00 dólares en 2024 a 21.61 en 2025 "
                          "y a 23.58 en 2026.",
    },
    {
        "tabla": "i3_flex_fare", "sql": "03_flex_fare.sql", "titulo": "I3 Viajes Flex Fare",
        "pregunta": "¿Qué parte de los viajes se pide con tarifa fija por aplicación?", "unidad": "% de los viajes",
        "interpretacion": "De enero a agosto, Flex Fare pasó del 9.0% al 19.6% y al 24.9% de los viajes amarillos. "
                          "En verdes se duplicó en 2026.",
    },
    {
        "tabla": "i4_efectivo", "sql": "04_efectivo.sql", "titulo": "I4 Viajes pagados en efectivo",
        "pregunta": "¿Se sigue usando el efectivo?", "unidad": "% de los viajes",
        "interpretacion": "El efectivo baja cada año. En amarillos pasa del 13.8% al 10.0% y al 9.1% de los viajes, "
                          "y en verdes del 27.8% al 23.2% y al 19.4%.",
    },
    {
        "tabla": "i5_propina_tarjeta", "sql": "05_propina_tarjeta.sql", "titulo": "I5 Propina con tarjeta",
        "pregunta": "¿Cuánta propina deja quien paga con tarjeta?", "unidad": "% de la tarifa",
        "interpretacion": "La propina con tarjeta se mantiene alrededor del 25% de la tarifa en amarillos y entre "
                          "el 22% y el 23% en verdes.",
    },
    {
        "tabla": "i6_cargo_cbd", "sql": "06_cargo_cbd.sql", "titulo": "I6 Viajes con cargo CBD",
        "pregunta": "¿A cuántos viajes alcanza el cobro por congestión de 2025?", "unidad": "% de los viajes",
        "interpretacion": "El cargo empezó el 5 de enero de 2025 y desde febrero lo paga cerca del 74% de los viajes "
                          "amarillos. En verdes no pasa del 11%.",
    },
    {
        "tabla": "i7_velocidad_manhattan", "sql": "07_velocidad_manhattan.sql", "titulo": "I7 Velocidad en Manhattan",
        "pregunta": "¿Cambió la velocidad de los viajes dentro de Manhattan?", "unidad": "Millas por hora",
        "interpretacion": "En amarillos la velocidad dentro de Manhattan subió poco en 2025. En 2026 quedó por debajo "
                          "de 2024 en los dos tipos de taxi.",
    },
    {
        "tabla": "i8_aeropuertos", "sql": "08_aeropuertos.sql", "titulo": "I8 Viajes de aeropuerto",
        "pregunta": "¿Qué peso tienen los viajes desde o hacia Newark, JFK y LaGuardia?", "unidad": "% de los viajes",
        "interpretacion": "Los viajes de aeropuerto pierden peso cada año, del 10.2% al 8.2% en amarillos y del 4.2% "
                          "al 3.4% en verdes.",
    },
    {
        "tabla": "i9_registros_excluidos", "sql": "09_registros_excluidos.sql", "titulo": "I9 Registros excluidos",
        "pregunta": "¿Qué parte de los registros de cada mes no pasa las reglas de calidad?", "unidad": "% de los registros",
        "interpretacion": "En 2025 se excluyó hasta el 12.9% de los registros amarillos por tarifas negativas del "
                          "proveedor 2. En 2024 y 2026 la cifra va del 3% al 6%.",
    },
]


def calcular_indicadores():
    # La base se crea de nuevo en cada ejecución para que refleje los archivos de data/raw
    BASE.parent.mkdir(parents=True, exist_ok=True)
    BASE.unlink(missing_ok=True)
    con = duckdb.connect()
    con.execute(f"SET file_search_path = '{RAIZ.as_posix()}'")
    con.execute((SQL / "vistas.sql").read_text(encoding="utf-8"))
    con.execute(f"ATTACH '{BASE.as_posix()}' AS tablero")
    for indicador in INDICADORES:
        consulta = (SQL / "indicadores" / indicador["sql"]).read_text(encoding="utf-8")
        inicio = time.perf_counter()
        con.execute(f"CREATE TABLE tablero.{indicador['tabla']} AS {consulta}")
        filas = con.execute(f"SELECT count(*) FROM tablero.{indicador['tabla']}").fetchone()[0]
        print(f"{indicador['tabla']}: {filas} filas en {time.perf_counter() - inicio:.1f} s")
    con.execute("DETACH tablero")
    con.close()


class Metabase:
    def __init__(self, url):
        self.url = url
        self.sesion = requests.Session()

    def pedir(self, metodo, ruta, **kwargs):
        respuesta = self.sesion.request(metodo, f"{self.url}/api/{ruta}", timeout=120, **kwargs)
        respuesta.raise_for_status()
        return respuesta.json() if respuesta.content else None

    def esperar(self):
        for _ in range(120):
            try:
                if self.pedir("GET", "health").get("status") == "ok":
                    return
            except requests.RequestException:
                pass
            time.sleep(5)
        raise SystemExit("Metabase no respondió en 10 minutos")

    def entrar(self):
        token = self.pedir("GET", "session/properties").get("setup-token")
        if token and not self.pedir("GET", "session/properties").get("has-user-setup"):
            self.pedir("POST", "setup", json={
                "token": token,
                "user": {"email": EMAIL, "password": CLAVE, "first_name": "Lab", "last_name": "DuckDB",
                         "site_name": "Laboratorio 8"},
                "prefs": {"site_name": "Laboratorio 8", "site_locale": "es", "allow_tracking": False},
            })
            print(f"Usuario administrador creado: {EMAIL}")
        sesion = self.pedir("POST", "session", json={"username": EMAIL, "password": CLAVE})
        self.sesion.headers["X-Metabase-Session"] = sesion["id"]

    def base_de_datos(self):
        detalles = {"database_file": BASE_METABASE, "read_only": True, "old_implicit_casting": True}
        for base in self.pedir("GET", "database")["data"]:
            if base["name"] == NOMBRE_BASE:
                self.pedir("PUT", f"database/{base['id']}", json={"details": detalles})
                return base["id"]
        base = self.pedir("POST", "database", json={"engine": "duckdb", "name": NOMBRE_BASE, "details": detalles})
        return base["id"]

    def archivar_anteriores(self):
        # Archiva las preguntas y el tablero de una ejecución anterior para no duplicarlos
        titulos = {i["titulo"] for i in INDICADORES}
        for tarjeta in self.pedir("GET", "card"):
            if tarjeta["name"] in titulos and not tarjeta.get("archived"):
                self.pedir("PUT", f"card/{tarjeta['id']}", json={"archived": True})
        for tablero in self.pedir("GET", "dashboard"):
            if tablero["name"] == NOMBRE_TABLERO and not tablero.get("archived"):
                self.pedir("PUT", f"dashboard/{tablero['id']}", json={"archived": True})

    def pregunta(self, base_id, indicador):
        etiqueta = {"id": str(uuid.uuid4()), "name": "taxi", "display-name": "Tipo de taxi", "type": "text",
                    "default": "yellow", "required": True}
        consulta = f"SELECT periodo, valor FROM {indicador['tabla']} WHERE taxi = {{{{taxi}}}} ORDER BY periodo"
        tarjeta = self.pedir("POST", "card", json={
            "name": indicador["titulo"],
            "description": indicador["pregunta"],
            "display": "line",
            "dataset_query": {"type": "native", "database": base_id,
                              "native": {"query": consulta, "template-tags": {"taxi": etiqueta}}},
            "visualization_settings": {
                "graph.dimensions": ["periodo"],
                "graph.metrics": ["valor"],
                "graph.x_axis.title_text": "Mes",
                "graph.y_axis.title_text": indicador["unidad"],
                "graph.y_axis.auto_range": True,
                "series_settings": {"valor": {"color": "#2a78d6", "title": indicador["unidad"], "line.missing": "none"}},
            },
        })
        return tarjeta["id"]

    def tablero(self, tarjetas):
        filtro = {"id": "taxi", "name": "Tipo de taxi", "slug": "taxi", "type": "string/=",
                  "sectionId": "string", "default": ["yellow"],
                  "values_source_type": "static-list", "values_source_config": {"values": ["yellow", "green"]}}
        tablero = self.pedir("POST", "dashboard", json={"name": NOMBRE_TABLERO, "parameters": [filtro]})
        encabezado = ("# Viajes de taxi en Nueva York\n"
                      "Indicadores mensuales de taxis amarillos (yellow) y verdes (green) calculados con DuckDB sobre los "
                      "Parquet de la TLC. El filtro de arriba cambia el tipo de taxi de todas las gráficas.")
        celdas = [self.texto(-1, 0, 0, 24, 3, encabezado)]
        siguiente = -2
        for n, (indicador, tarjeta_id) in enumerate(zip(INDICADORES, tarjetas)):
            fila, columna = 3 + (n // 3) * 11, (n % 3) * 8
            celdas.append({
                "id": siguiente, "card_id": tarjeta_id, "row": fila, "col": columna, "size_x": 8, "size_y": 6,
                "parameter_mappings": [{"parameter_id": "taxi", "card_id": tarjeta_id,
                                        "target": ["variable", ["template-tag", "taxi"]]}],
                "visualization_settings": {},
            })
            texto = f"**{indicador['pregunta']}**\n\n{indicador['interpretacion']}"
            celdas.append(self.texto(siguiente - 1, fila + 6, columna, 8, 5, texto))
            siguiente -= 2
        self.pedir("PUT", f"dashboard/{tablero['id']}", json={"dashcards": celdas, "parameters": [filtro]})
        return tablero["id"]

    @staticmethod
    def texto(id_, fila, columna, ancho, alto, contenido):
        return {
            "id": id_, "card_id": None, "row": fila, "col": columna, "size_x": ancho, "size_y": alto,
            "parameter_mappings": [],
            "visualization_settings": {
                "virtual_card": {"name": None, "display": "text", "visualization_settings": {},
                                 "dataset_query": {}, "archived": False},
                "text": contenido,
            },
        }


def main():
    calcular_indicadores()
    metabase = Metabase(METABASE)
    metabase.esperar()
    metabase.entrar()
    base_id = metabase.base_de_datos()
    metabase.pedir("POST", f"database/{base_id}/sync_schema")
    metabase.archivar_anteriores()
    tarjetas = [metabase.pregunta(base_id, indicador) for indicador in INDICADORES]
    tablero_id = metabase.tablero(tarjetas)
    print(f"Tablero listo en http://localhost:3000/dashboard/{tablero_id}")


if __name__ == "__main__":
    main()

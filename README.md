# Lab 8 - DuckDB

Viajes de taxis amarillos y verdes de Nueva York de 2024 a 2026, analizados con DuckDB sobre los Parquet de la [TLC](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page). CC3084 Data Science, UVG, ciclo 2 de 2026.

## Integrantes

- Javier Eduardo España (23361)
- Angel Esteban Esquit (23221)
- Roberto Jose Barreda (23354)

## Ejecución

Requiere Docker con Compose y cerca de 10 GB libres.

```bash
git clone https://github.com/bar23354/DS-Lab08.git
cd DS-Lab08
docker compose up -d --build
docker compose exec lab bash
```

Las consultas leen todo lo que hay en data/raw, así que los años se agregan en el orden del enunciado para repetir los resultados de cada notebook.

```bash
# Ejercicios 2 a 4, con 2026
python scripts/download_data.py --anios 2026
python scripts/verificar_descarga.py --anios 2026
jupyter nbconvert --to notebook --execute --inplace notebooks/0[34]_*.ipynb

# Ejercicios 5 a 7, con 2024 y 2026
python scripts/download_data.py --anios 2024 2026
python scripts/benchmark.py
jupyter nbconvert --to notebook --execute --inplace notebooks/0[567]_*.ipynb

# Ejercicio 8, con 2024, 2025 y 2026
python scripts/download_data.py
python scripts/tablero_metabase.py
jupyter nbconvert --to notebook --execute --inplace notebooks/08_*.ipynb
```

JupyterLab queda en http://localhost:8888 y el tablero en http://localhost:3000, con el usuario lab8@uvg.edu.gt y la clave lab8-duckdb-2026.

## Respuestas

Cada archivo lleva el número de su ejercicio. Los ejercicios 1, 2 y 9 están en [docs](docs) en Word y PDF, los ejercicios 3 a 8 en [notebooks](notebooks), las consultas en [sql](sql) y las salidas de cada ejecución en [docs/evidencias](docs/evidencias).

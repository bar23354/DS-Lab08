# Parte 4. Exploración con DuckDB

Consultas directas sobre los Parquet de 2026 y análisis exploratorio, ejercicios 3 y 4.

## Ejecución

```bash
cd 04_exploracion
docker compose up -d --build
docker compose exec lab python scripts/download_data.py
docker compose exec lab jupyter nbconvert --to notebook --execute --inplace notebooks/03_consultas_parquet.ipynb
docker compose exec lab jupyter nbconvert --to notebook --execute --inplace notebooks/04_analisis_exploratorio.ipynb
```

Los notebooks se pueden ejecutar desde JupyterLab en http://localhost:8888.

| Notebook | Contenido |
| --- | --- |
| 03_consultas_parquet | Archivos, registros, columnas, tipos, muestra y calidad de datos |
| 04_analisis_exploratorio | Preguntas, consultas, resultados y hallazgos |

Las consultas están en sql/ej3 y sql/ej4, y sql/vistas.sql define las vistas viajes, viajes_validos y zonas. La descarga agrega el catálogo de zonas de la TLC.

# Parte 5. Incorporación de 2024 y benchmark

Datos de 2024 agregados al sistema y comparación de consultas sobre Parquet contra una tabla de DuckDB, ejercicios 5 y 6.

## Ejecución

```bash
cd 05_incremental_benchmark
docker compose up -d --build
docker compose exec lab python scripts/download_data.py
docker compose exec lab python scripts/verificar_descarga.py
docker compose exec lab python scripts/benchmark.py
docker compose exec lab jupyter nbconvert --to notebook --execute --inplace notebooks/05_incorporacion_2024.ipynb
docker compose exec lab jupyter nbconvert --to notebook --execute --inplace notebooks/06_benchmark.ipynb
```

Si se copia data/raw de la parte 4, la descarga trae 2024 y omite 2026. El benchmark crea bases de DuckDB en data/processed y guarda los tiempos en docs/benchmark_tablas.csv y docs/benchmark_tiempos.csv.

| Notebook | Contenido |
| --- | --- |
| 05_incorporacion_2024 | Descarga, verificación, consultas conjuntas y revisión de las consultas anteriores |
| 06_benchmark | Diseño, consultas, tiempos, análisis y escenarios del benchmark |

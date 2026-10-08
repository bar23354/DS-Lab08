# Parte 2. Descarga de datos

Modificación del script de descarga del repositorio base para los taxis amarillos y verdes de 2026, incisos 2.1 a 2.4.

## Ejecución

```bash
cd 02_descarga
docker compose up -d --build
docker compose exec lab python scripts/download_data.py
```

Los archivos quedan en data/raw, en una carpeta por tipo de taxi y año. Los que ya existen y están completos no se descargan otra vez.

El análisis del script proporcionado y los cambios están en docs/descarga.md.

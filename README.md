# Parte 3. Verificación de la descarga

Ejecución de la descarga de 2026 y revisión de que el conjunto esté completo, incisos 2.5 a 2.7.

## Ejecución

```bash
cd 03_verificacion
docker compose up -d --build
docker compose exec lab python scripts/download_data.py
docker compose exec lab python scripts/verificar_descarga.py
```

El detalle por archivo queda en docs/verificacion_descarga.csv. Los resultados, los cambios al script y el criterio de completitud están en docs/verificacion.md.

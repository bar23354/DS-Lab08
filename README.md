# Parte 1. Ambiente

Ambiente de Docker del repositorio base, con JupyterLab y Metabase, para el ejercicio 1.

## Levantar el ambiente

Requiere Docker con Compose.

```bash
cd 01_ambiente
docker compose up -d --build
docker compose exec lab python scripts/verificar_ambiente.py
```

JupyterLab queda en http://localhost:8888 y Metabase en http://localhost:3000. Los servicios se detienen con docker compose down.

La estructura del proyecto, las herramientas y la verificación del ambiente están en docs/ambiente.md.

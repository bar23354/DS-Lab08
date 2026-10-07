# Ambiente

## Estructura del proyecto

| Ruta | Propósito |
| --- | --- |
| data/raw | Parquet de la TLC tal como se descargan, en una carpeta por tipo de taxi y año. Git los ignora |
| data/processed | Bases de DuckDB y archivos derivados. Git los ignora |
| notebooks | Consultas, resultados e interpretación de cada ejercicio |
| scripts | Procesos de terminal: descarga, verificación y benchmark |
| sql | Consultas que usan los notebooks, los scripts y Metabase |
| docs | Respuestas y evidencias |
| Dockerfile | Imagen del servicio lab con Python 3.11 y las librerías de requirements.txt |
| metabase.Dockerfile | Imagen de Metabase con el driver de DuckDB, sobre Debian porque el driver necesita glibc |
| docker-compose.yml | Servicios lab y metabase, con data, notebooks, scripts, sql y docs montados en /workspace |
| requirements.txt | Versiones fijas de las librerías de Python, con duckdb en la misma versión que el driver de Metabase |

Las carpetas se montan como volúmenes, así que lo que se descarga o se genera dentro de los contenedores queda en la carpeta local. Dentro del ambiente los datos están en /workspace/data.

El equipo agregó .dockerignore para que la construcción no envíe los datos a Docker. Las imágenes no los necesitan: la del servicio lab copia requirements.txt y la de Metabase no copia archivos del proyecto.

## Levantar el ambiente (1.1 y 1.2)

El trabajo parte de un fork de github.com/menene/duckdb. Con el fork clonado:

```bash
cd 01_ambiente
docker compose up -d --build
```

La primera construcción descarga la imagen de Python, la de Java y el jar de Metabase, cerca de 3 GB en total.

## Servicios (1.3)

| Servicio | Puerto | Uso |
| --- | --- | --- |
| lab | 8888 | JupyterLab, Python y DuckDB |
| metabase | 3000 | Metabase con el driver de DuckDB |

Los puertos se publican en 127.0.0.1, por eso JupyterLab no pide token.

| Prueba | Resultado |
| --- | --- |
| docker compose ps | lab8-lab y lab8-metabase en estado running |
| JupyterLab en http://localhost:8888 | Responde con código 200 |
| Metabase en http://localhost:3000/api/health | Responde ok |
| scripts/verificar_ambiente.py dentro de lab | Python 3.11.14 en Linux, versiones de requirements.txt, DuckDB escribe y lee Parquet, estructura completa y Metabase alcanzable desde lab |

La salida completa de estas pruebas está en verificacion_ambiente.txt.

## Herramientas disponibles (1.4)

| Herramienta | Versión | Uso |
| --- | --- | --- |
| Python | 3.11.14 | Lenguaje de scripts y notebooks |
| DuckDB | 1.5.5 | Consultas SQL sobre Parquet y base local |
| pandas | 3.0.6 | Tablas de resultados |
| PyArrow | 25.0.1 | Soporte de Parquet y Arrow para pandas |
| matplotlib | 3.11.2 | Gráficas en los notebooks |
| requests | 2.34.2 | Descarga de archivos y llamadas a la API de Metabase |
| JupyterLab | 4.6.4 | Notebooks |
| Metabase | v0.63.19 | Tablero de indicadores |
| Driver de DuckDB para Metabase | 1.5.5.0 | Conexión de Metabase con las bases de DuckDB |
| Java (Eclipse Temurin) | 21 | Ejecución de Metabase |

## Ambiente reproducible (1.6)

El ambiente queda definido en archivos del repositorio. Cada integrante y el docente ejecutan el proyecto con la misma versión de Python, de DuckDB, de Metabase y de cada librería, sin depender de lo instalado en su computadora. Si un resultado cambia, la causa está en los datos o en el código y no en la instalación.

En este laboratorio importa por tres razones. Los datos crecen con cada año agregado y el análisis se vuelve a ejecutar varias veces. Los tiempos del benchmark dependen de la versión de DuckDB. Y Metabase lee las bases con su propio driver, que tiene que coincidir con la versión de DuckDB que las crea.

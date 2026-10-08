# Verificación de la descarga

## Ejecución (2.5)

El script modificado se ejecutó dos veces dentro del servicio lab, la primera con data/raw vacía. La salida completa está en descarga_2026.txt.

| Ejecución | Descargados | Ya existían | No publicados | Fallidos |
| --- | --- | --- | --- | --- |
| Primera | 16 | 0 | 8 | 0 |
| Segunda | 0 | 16 | 8 | 0 |

La segunda ejecución no descargó archivos. Los 8 no publicados son septiembre a diciembre de 2026 de cada tipo, que la TLC no había publicado al 6 de octubre de 2026.

Después, verificar_descarga.py dio este resultado:

| Tipo | Archivos | Meses | Registros | Tamaño |
| --- | --- | --- | --- | --- |
| yellow | 8 | enero a agosto | 29,703,355 | 511.5 MB |
| green | 8 | enero a agosto | 337,114 | 8.3 MB |

Los 16 archivos publicados están completos. El detalle por archivo está en verificacion_descarga.csv.

## Cambios al script (2.6)

| Parte | Script proporcionado | Script modificado |
| --- | --- | --- |
| Años | Constante ANIO = 2026 | Lista ANIOS y opción --anios |
| Destino | Ruta relativa a la carpeta de trabajo | Ruta calculada desde la ubicación del script |
| Archivo existente | Se omite si pesa más de cero bytes | Se omite si es un Parquet completo, y si no se descarga de nuevo |
| Consulta al servidor | Un error de red cuenta como mes no publicado | Un 403 o 404 cuenta como no publicado y un error de red como fallido |
| Tamaño descargado | Se revisa que no sea cero | Se compara con el tamaño que informa el servidor |
| Mensajes | Año fijo en el texto | Tipo y año de cada archivo |

## Completitud (2.7)

El script verificar_descarga.py toma los años, los tipos y las rutas de download_data.py y revisa cada archivo en tres pasos:

1. Toma como referencia los archivos enlazados en la página de datos de la TLC, una fuente distinta del servidor que usa la descarga. Para 2026 la página enlaza enero a agosto de yellow y green.
2. Compara los bytes en disco con el tamaño que informa el servidor. Un archivo cortado tiene menos bytes.
3. Lee con DuckDB el pie del Parquet y obtiene su número de registros. Un archivo dañado o una página de error guardada como Parquet falla en este paso.

El script marca como no publicado cualquier Parquet de data/raw que no esté en la lista de la TLC, y termina con código 1 si algún archivo no está completo.

Para probar el criterio se cortó green_tripdata_2026-02.parquet, se borró green_tripdata_2026-03.parquet y se guardó una página de error como yellow_tripdata_2026-09.parquet. La verificación reportó tamaño distinto, falta y no publicado, con 14 de 16 archivos completos. Al ejecutar la descarga, el script detectó el archivo cortado por la falta de la marca PAR1, lo descargó de nuevo junto con el faltante y dejó septiembre como no publicado. Después de borrar la página de error, la verificación volvió a 16 de 16. La salida está en prueba_errores.txt.

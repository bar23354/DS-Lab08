# Descarga de datos

## Script proporcionado (2.1)

El script scripts/download_data.py del repositorio base ya recorre los doce meses de 2026 para taxis amarillos y verdes, pregunta al servidor si cada mes está publicado, omite los archivos que existen y descarga sobre un nombre temporal. Al revisarlo aparecieron estas partes a modificar:

1. Si la consulta al servidor falla por la red, la función esta_publicado devuelve False y el mes se reporta como no publicado. Un corte de conexión hace que falten archivos sin que el resumen lo muestre como error.
2. Después de descargar, el script revisa que el archivo no quede vacío pero no compara los bytes recibidos con el tamaño que informa el servidor, así que una transferencia cortada sin error se acepta.
3. Un archivo local se da por bueno si su tamaño es mayor que cero. Un Parquet dañado o una página de error guardada con ese nombre nunca se vuelve a descargar.
4. La carpeta de destino es la ruta relativa data/raw. Si el script se ejecuta desde otra carpeta, los archivos quedan fuera de la estructura del proyecto.
5. El año está fijo en la constante ANIO y en los mensajes. Para descargar 2024 o 2025 hay que editar varias partes del código.

## Script modificado (2.2 a 2.4)

- Los años están en la lista ANIOS, que vale (2026,), y la opción --anios permite pedir otros sin editar el código. Para cada tipo y año recorre los doce meses y arma el nombre y la URL con el patrón de la TLC.
- La ruta de destino se calcula desde la ubicación del script, así que los archivos quedan en data/raw, en una carpeta por tipo y año, aunque el script se ejecute desde otra carpeta.
- Un archivo local se omite si es un Parquet completo, es decir, si empieza y termina con la marca PAR1. Si existe pero no la tiene, se descarga de nuevo.
- La consulta al servidor devuelve el tamaño del archivo. Un 403 o 404 se reporta como no publicado y un error de red se reporta como fallido.
- La descarga compara los bytes recibidos con el tamaño del servidor antes de renombrar el archivo temporal y hace hasta tres intentos.
- El resumen final y el código de salida 1 cuando algo falla quedan igual que en el script original.

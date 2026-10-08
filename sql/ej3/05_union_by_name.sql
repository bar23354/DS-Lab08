-- Columnas que DuckDB expone al leer todos los archivos amarillos con y sin union_by_name
SELECT
    'sin union_by_name' AS lectura,
    count(*) AS columnas,
    list_contains(list(column_name), 'request_source') AS incluye_request_source
FROM (DESCRIBE SELECT * FROM read_parquet('data/raw/yellow/*/*.parquet'))
UNION ALL
SELECT
    'con union_by_name',
    count(*),
    list_contains(list(column_name), 'request_source')
FROM (DESCRIBE SELECT * FROM read_parquet('data/raw/yellow/*/*.parquet', union_by_name = true))

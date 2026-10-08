-- Tipo, rango, cuartiles y porcentaje de nulos de cada columna de los viajes verdes
SUMMARIZE SELECT * FROM read_parquet('data/raw/green/*/*.parquet', union_by_name = true)

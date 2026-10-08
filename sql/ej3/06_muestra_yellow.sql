-- Muestra aleatoria reproducible de viajes amarillos
SELECT *
FROM read_parquet('data/raw/yellow/*/*.parquet', union_by_name = true)
USING SAMPLE bernoulli(0.00002%) REPEATABLE (42)

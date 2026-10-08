-- Relación entre la forma de pago y los nulos en pasajeros, código de tarifa y recargos
WITH viajes AS (
    SELECT 'yellow' AS taxi, payment_type, passenger_count, RatecodeID, congestion_surcharge
    FROM read_parquet('data/raw/yellow/*/*.parquet', union_by_name = true)
    UNION ALL
    SELECT 'green', payment_type, passenger_count, RatecodeID, congestion_surcharge
    FROM read_parquet('data/raw/green/*/*.parquet', union_by_name = true)
)
SELECT
    taxi,
    payment_type,
    count(*) AS viajes,
    round(100 * count(*) / sum(count(*)) OVER (PARTITION BY taxi), 2) AS pct_viajes,
    count(*) FILTER (WHERE passenger_count IS NULL) AS sin_passenger_count,
    count(*) FILTER (WHERE RatecodeID IS NULL) AS sin_ratecode,
    count(*) FILTER (WHERE congestion_surcharge IS NULL) AS sin_congestion
FROM viajes
GROUP BY taxi, payment_type
ORDER BY taxi, payment_type
